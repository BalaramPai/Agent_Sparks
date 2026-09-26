from __future__ import annotations

import threading
from typing import Callable

import numpy as np
from faster_whisper import WhisperModel

from .streaming import StreamingTranscriptionResult, StreamingTranscriptionType


class IncrementalFasterWhisperSTT:
    """
    Near-streaming Faster-Whisper adapter.

    Accumulates audio and periodically performs inference to produce
    partial transcription results. Final transcription is produced
    when finish() is called.
    """

    def __init__(
        self,
        *,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
        language: str | None = None,
        beam_size: int = 1,
        sample_rate: int = 16_000,
        partial_interval: float = 0.8,
        min_audio_duration: float = 0.8,
    ) -> None:
        if partial_interval <= 0:
            raise ValueError("partial_interval must be positive")

        if min_audio_duration <= 0:
            raise ValueError("min_audio_duration must be positive")

        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.language = language
        self.beam_size = beam_size
        self.sample_rate = sample_rate
        self.partial_interval = partial_interval
        self.min_audio_duration = min_audio_duration

        self._model: WhisperModel | None = None
        self._audio = bytearray()
        self._callback: Callable | None = None

        self._running = False
        self._cancelled = False

        self._worker: threading.Thread | None = None
        self._wake_event = threading.Event()
        self._lock = threading.Lock()

        self._sequence = 0
        self._last_partial = ""

    def load(self) -> None:
        if self._model is None:
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )

    @property
    def is_active(self) -> bool:
        with self._lock:
            return self._running

    def start(self) -> None:
        if self.is_active:
            return

        self.load()

        with self._lock:
            self._audio.clear()
            self._cancelled = False
            self._sequence = 0
            self._last_partial = ""
            self._running = True

        self._callback = None
        self._wake_event.clear()

        self._worker = threading.Thread(
            target=self._partial_loop,
            name="sparks-whisper-stream",
            daemon=True,
        )
        self._worker.start()

    def push_audio(self, audio: bytes) -> None:
        if not self.is_active:
            raise RuntimeError("streaming STT is not active")

        if not audio:
            return

        with self._lock:
            self._audio.extend(audio)

        self._wake_event.set()

    def finish(self, callback) -> None:
        if not self.is_active:
            raise RuntimeError("streaming STT is not active")

        self._callback = callback

        # Tell the background worker to stop.
        with self._lock:
            self._running = False

        self._wake_event.set()

        worker = self._worker

        if worker is not None:
            worker.join(timeout=5.0)

            if worker.is_alive():
                raise RuntimeError(
                    "streaming STT worker failed to stop"
                )

        if self._cancelled:
            self._cleanup()
            return

        # Final inference happens synchronously after the worker
        # has completely stopped.
        result = self._transcribe_current()

        if result:
            self._emit(
                result,
                StreamingTranscriptionType.FINAL,
            )

        self._cleanup()

    def cancel(self) -> None:
        with self._lock:
            self._cancelled = True
            self._running = False

        self._wake_event.set()

        worker = self._worker

        if worker is not None and worker.is_alive():
            worker.join(timeout=2.0)

        self._cleanup()

    def _partial_loop(self) -> None:
        while True:
            triggered = self._wake_event.wait(
                timeout=self.partial_interval
            )

            self._wake_event.clear()

            with self._lock:
                running = self._running
                cancelled = self._cancelled

            if not running or cancelled:
                return

            duration = self._audio_duration()

            if duration < self.min_audio_duration:
                continue

            text = self._transcribe_current()

            if not text:
                continue

            if text == self._last_partial:
                continue

            self._last_partial = text

            self._emit(
                text,
                StreamingTranscriptionType.PARTIAL,
            )

    def _transcribe_current(self) -> str:
        model = self._model

        if model is None:
            return ""

        with self._lock:
            audio = bytes(self._audio)

        if not audio:
            return ""

        samples = (
            np.frombuffer(
                audio,
                dtype=np.int16,
            ).astype(np.float32)
            / 32768.0
        )

        segments, _ = model.transcribe(
            samples,
            language=self.language,
            beam_size=self.beam_size,
            vad_filter=False,
            condition_on_previous_text=False,
        )

        return " ".join(
            segment.text.strip()
            for segment in segments
            if segment.text.strip()
        ).strip()

    def _audio_duration(self) -> float:
        with self._lock:
            byte_count = len(self._audio)

        return byte_count / (self.sample_rate * 2)

    def _emit(
        self,
        text: str,
        result_type: StreamingTranscriptionType,
    ) -> None:
        callback = self._callback

        if callback is None:
            return

        with self._lock:
            sequence = self._sequence
            self._sequence += 1

        callback(
            StreamingTranscriptionResult(
                text=text,
                result_type=result_type,
                sequence=sequence,
            )
        )

    def _cleanup(self) -> None:
        with self._lock:
            self._running = False

        self._wake_event.set()
        self._worker = None
        self._callback = None
