from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import Callable

from sparks.voice.cancellation import CancellationError, CancellationToken
from sparks.voice.capture.base import AudioCapture, AudioCaptureConfig
from sparks.voice.interruption import (
    InterruptionController,
    InterruptionReason,
)
from sparks.voice.stt.base import SpeechToText
from sparks.voice.stt.types import TranscriptionResult, TranscriptionType
from sparks.voice.stt.streaming import (
    StreamingTranscriptionResult,
    StreamingTranscriptionType,
)
from sparks.voice.types import VoiceEvent, VoiceEventType, VoiceState
from sparks.voice.vad.base import VoiceActivityFrame
from sparks.voice.vad.engine import VadEngine
from sparks.voice.wakeword.gate import VoiceActivationGate


class VoicePipeline:
    """
    Coordinates microphone capture, activation, VAD and STT.

    Supports two STT execution modes:

    1. Existing utterance-level SpeechToText fallback.
    2. Optional incremental streaming STT.

    Streaming mode remains provider-independent.
    """

    def __init__(
        self,
        capture: AudioCapture,
        vad: VadEngine,
        stt: SpeechToText,
        *,
        streaming_stt=None,
        capture_config: AudioCaptureConfig | None = None,
        activation_gate: VoiceActivationGate | None = None,
        pre_roll_frames: int = 3,
        event_callback: Callable[[VoiceEvent], None] | None = None,
    ) -> None:
        if pre_roll_frames < 0:
            raise ValueError("pre_roll_frames must be >= 0")

        self.capture = capture
        self.vad = vad
        self.stt = stt
        self.streaming_stt = streaming_stt

        self.capture_config = (
            capture_config or AudioCaptureConfig()
        )

        self.activation_gate = activation_gate
        self.pre_roll_frames = pre_roll_frames
        self.event_callback = event_callback

        self._state = VoiceState.IDLE
        self._running = False

        self._utterance: list[bytes] = []
        self._pre_roll: list[bytes] = []

        self._utterance_authorized = False

        self._compat_vad_speaking = False

        self._executor: ThreadPoolExecutor | None = None
        self._lock = Lock()

        self._cancellation_token: CancellationToken | None = None

        self._streaming_active = False

        self.interruption = InterruptionController(
            self.cancel_transcription
        )

    @property
    def state(self) -> VoiceState:
        return self._state

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_transcribing(self) -> bool:
        return self._state == VoiceState.TRANSCRIBING

    @property
    def is_streaming(self) -> bool:
        return self._streaming_active

    @property
    def cancellation_token(self) -> CancellationToken | None:
        return self._cancellation_token

    def start(self) -> None:
        with self._lock:
            if self._running:
                return

            self._running = True
            self._state = VoiceState.LISTENING

            self._executor = ThreadPoolExecutor(
                max_workers=1,
                thread_name_prefix="sparks-stt",
            )

            self.vad.reset()

            self._utterance.clear()
            self._pre_roll.clear()

            self._utterance_authorized = False
            self._compat_vad_speaking = False

            self._cancellation_token = None
            self._streaming_active = False

            self.interruption.reset()

            if self.activation_gate is not None:
                self.activation_gate.reset()

        self._emit(
            VoiceEvent(
                event_type=VoiceEventType.LISTENING_STARTED,
                state=VoiceState.LISTENING,
            )
        )

        try:
            self.capture.start(self._on_audio)

        except Exception as exc:
            with self._lock:
                self._running = False
                self._state = VoiceState.ERROR

            self._emit(
                VoiceEvent(
                    event_type=VoiceEventType.ERROR,
                    state=VoiceState.ERROR,
                    metadata={
                        "error": str(exc),
                        "error_type": type(exc).__name__,
                    },
                )
            )

            raise

    def stop(self) -> None:
        with self._lock:
            if not self._running:
                self._state = VoiceState.IDLE
                return

            self._running = False
            self._state = VoiceState.IDLE

            executor = self._executor
            self._executor = None

            token = self._cancellation_token
            self._cancellation_token = None

            streaming_active = self._streaming_active
            self._streaming_active = False

            self._utterance.clear()
            self._pre_roll.clear()

            self._utterance_authorized = False
            self._compat_vad_speaking = False

        if token is not None:
            token.cancel()

        try:
            self.capture.stop()

        finally:
            if streaming_active and self.streaming_stt is not None:
                self.streaming_stt.cancel()

            self.stt.cancel()

            self.vad.reset()

            if self.activation_gate is not None:
                self.activation_gate.reset()

            if executor is not None:
                executor.shutdown(
                    wait=False,
                    cancel_futures=True,
                )

    def cancel_transcription(self) -> bool:
        with self._lock:
            token = self._cancellation_token
            streaming_active = self._streaming_active

            if (
                token is None
                or self._state != VoiceState.TRANSCRIBING
            ):
                return False

            token.cancel()

            self._streaming_active = False

        if streaming_active and self.streaming_stt is not None:
            self.streaming_stt.cancel()

        self.stt.cancel()

        return True

    def interrupt(
        self,
        reason: InterruptionReason = InterruptionReason.USER_SPEECH,
        *,
        source: str = "voice",
    ) -> bool:
        return self.interruption.interrupt(
            reason,
            source=source,
        )

    def _on_audio(self, audio: bytes) -> None:
        if not self._running:
            return

        try:
            activation_active = self._process_activation(audio)

            frame = VoiceActivityFrame(
                audio=audio,
                sample_rate=self.capture_config.sample_rate,
                duration_ms=self._frame_duration_ms(),
            )

            vad_result = self.vad.process(frame)

            speech_started, speech_stopped = (
                self._interpret_vad_result(vad_result)
            )

            if (
                speech_started
                and self._state == VoiceState.TRANSCRIBING
            ):
                self.interrupt(
                    InterruptionReason.USER_SPEECH,
                    source="vad",
                )

            # While an active streaming transcription is running,
            # every incoming frame is forwarded immediately.
            if (
                self._streaming_active
                and self._state == VoiceState.TRANSCRIBING
                and not speech_started
                and not speech_stopped
            ):
                self.streaming_stt.push_audio(audio)
                return

            if speech_started:
                self._handle_speech_started(
                    audio,
                    activation_active,
                )
                return

            if self._state == VoiceState.DETECTING_SPEECH:
                self._utterance.append(audio)

                if self._streaming_active:
                    self.streaming_stt.push_audio(audio)

            if speech_stopped:
                self._handle_speech_stopped()
                return

            if self._state != VoiceState.DETECTING_SPEECH:
                self._update_pre_roll(audio)

        except Exception as exc:
            with self._lock:
                self._state = VoiceState.ERROR

            self._emit(
                VoiceEvent(
                    event_type=VoiceEventType.ERROR,
                    state=VoiceState.ERROR,
                    metadata={
                        "error": str(exc),
                        "error_type": type(exc).__name__,
                    },
                )
            )

    def _interpret_vad_result(
        self,
        result,
    ) -> tuple[bool, bool]:
        if isinstance(result, bool):
            speech = result

            speech_started = (
                speech
                and not self._compat_vad_speaking
            )

            speech_stopped = (
                not speech
                and self._compat_vad_speaking
            )

            self._compat_vad_speaking = speech

            return speech_started, speech_stopped

        if result is None:
            return False, False

        event_type = getattr(result, "event_type", None)

        if event_type is None:
            event_type = getattr(result, "type", None)

        if event_type is None:
            return False, False

        value = getattr(event_type, "value", event_type)

        return (
            value == "speech_started",
            value == "speech_stopped",
        )

    def _process_activation(self, audio: bytes) -> bool:
        if self.activation_gate is None:
            return True

        self.activation_gate.process(audio)

        return self.activation_gate.is_active

    def _handle_speech_started(
        self,
        audio: bytes,
        activation_active: bool,
    ) -> None:
        self._utterance_authorized = activation_active
        self._utterance.clear()

        if self._utterance_authorized:
            self._utterance.extend(self._pre_roll)
            self._utterance.append(audio)

        with self._lock:
            self._state = VoiceState.DETECTING_SPEECH

        self._emit(
            VoiceEvent(
                event_type=VoiceEventType.SPEECH_STARTED,
                state=VoiceState.DETECTING_SPEECH,
                metadata={
                    "activated": self._utterance_authorized,
                },
            )
        )

        if (
            self._utterance_authorized
            and self.streaming_stt is not None
        ):
            self._start_streaming_transcription()

    def _start_streaming_transcription(self) -> None:
        if self.streaming_stt is None:
            return

        with self._lock:
            if not self._running:
                return

            self._state = VoiceState.TRANSCRIBING
            self._streaming_active = True

            token = CancellationToken()
            self._cancellation_token = token

        self._emit(
            VoiceEvent(
                event_type=VoiceEventType.TRANSCRIPTION_STARTED,
                state=VoiceState.TRANSCRIBING,
                metadata={
                    "streaming": True,
                },
            )
        )

        try:
            self.streaming_stt.start()

            for audio in self._utterance:
                token.throw_if_cancelled()
                self.streaming_stt.push_audio(audio)

        except CancellationError:
            self._finish_streaming_state(token)

        except Exception:
            with self._lock:
                self._streaming_active = False

            raise

    def _handle_speech_stopped(self) -> None:
        self._emit(
            VoiceEvent(
                event_type=VoiceEventType.SPEECH_STOPPED,
                state=self._state,
                metadata={
                    "activated": self._utterance_authorized,
                },
            )
        )

        if not self._utterance_authorized:
            self._utterance.clear()
            self._utterance_authorized = False

            with self._lock:
                if self._running:
                    self._state = VoiceState.LISTENING

            return

        if self._streaming_active:
            self._finish_streaming_transcription()
            return

        audio_chunks = tuple(self._utterance)

        self._utterance.clear()
        self._utterance_authorized = False

        if not audio_chunks:
            with self._lock:
                if self._running:
                    self._state = VoiceState.LISTENING

            return

        self._dispatch_transcription(audio_chunks)

    def _finish_streaming_transcription(self) -> None:
        streaming_stt = self.streaming_stt
        token = self._cancellation_token

        if streaming_stt is None or token is None:
            return

        try:
            token.throw_if_cancelled()

            def handle_result(
                result: StreamingTranscriptionResult,
            ) -> None:
                token.throw_if_cancelled()

                if (
                    result.result_type
                    == StreamingTranscriptionType.PARTIAL
                ):
                    event_type = (
                        VoiceEventType.TRANSCRIPTION_PARTIAL
                    )
                else:
                    event_type = (
                        VoiceEventType.TRANSCRIPTION_COMPLETED
                    )

                self._emit(
                    VoiceEvent(
                        event_type=event_type,
                        state=VoiceState.TRANSCRIBING,
                        text=result.text,
                        confidence=result.confidence,
                        metadata={
                            "streaming": True,
                            "sequence": result.sequence,
                        },
                    )
                )

            streaming_stt.finish(handle_result)

            self._finish_streaming_state(token)

        except CancellationError:
            self._finish_streaming_state(token)

        except Exception:
            with self._lock:
                self._streaming_active = False

            raise

    def _finish_streaming_state(
        self,
        token: CancellationToken,
    ) -> None:
        with self._lock:
            if self._cancellation_token is token:
                self._cancellation_token = None

            self._streaming_active = False

            if self._running:
                self._state = VoiceState.LISTENING

        self._utterance.clear()
        self._utterance_authorized = False

    def _dispatch_transcription(
        self,
        audio_chunks: tuple[bytes, ...],
    ) -> None:
        with self._lock:
            if not self._running:
                return

            self._state = VoiceState.TRANSCRIBING

            token = CancellationToken()
            self._cancellation_token = token

            executor = self._executor

        if executor is None:
            return

        self._emit(
            VoiceEvent(
                event_type=VoiceEventType.TRANSCRIPTION_STARTED,
                state=VoiceState.TRANSCRIBING,
            )
        )

        executor.submit(
            self._transcribe,
            audio_chunks,
            token,
        )

    def _transcribe(
        self,
        audio_chunks: tuple[bytes, ...],
        token: CancellationToken,
    ) -> None:
        try:
            token.throw_if_cancelled()

            def handle_result(
                result: TranscriptionResult,
            ) -> None:
                token.throw_if_cancelled()

                if result.result_type == TranscriptionType.PARTIAL:
                    event_type = VoiceEventType.TRANSCRIPTION_PARTIAL
                else:
                    event_type = (
                        VoiceEventType.TRANSCRIPTION_COMPLETED
                    )

                self._emit(
                    VoiceEvent(
                        event_type=event_type,
                        state=VoiceState.TRANSCRIBING,
                        text=result.text,
                        confidence=result.confidence,
                    )
                )

            self.stt.transcribe(
                audio_chunks,
                callback=handle_result,
            )

            token.throw_if_cancelled()

            with self._lock:
                if (
                    self._running
                    and self._cancellation_token is token
                ):
                    self._state = VoiceState.LISTENING
                    self._cancellation_token = None

        except CancellationError:
            with self._lock:
                if self._cancellation_token is token:
                    self._cancellation_token = None

                if self._running:
                    self._state = VoiceState.LISTENING

        except Exception as exc:
            with self._lock:
                if self._cancellation_token is token:
                    self._cancellation_token = None

                if self._running:
                    self._state = VoiceState.ERROR

            self._emit(
                VoiceEvent(
                    event_type=VoiceEventType.ERROR,
                    state=VoiceState.ERROR,
                    metadata={
                        "error": str(exc),
                        "error_type": type(exc).__name__,
                    },
                )
            )

    def _update_pre_roll(self, audio: bytes) -> None:
        if self.pre_roll_frames == 0:
            return

        self._pre_roll.append(audio)

        if len(self._pre_roll) > self.pre_roll_frames:
            self._pre_roll.pop(0)

    def _frame_duration_ms(self) -> int:
        return int(
            self.capture_config.block_size
            / self.capture_config.sample_rate
            * 1000
        )

    def _emit(self, event: VoiceEvent) -> None:
        if self.event_callback is not None:
            self.event_callback(event)
