from __future__ import annotations

from threading import Lock

from sparks.voice.cancellation import CancellationToken
from sparks.voice.stt.streaming import StreamingTranscriptionResult
from sparks.voice.stt.streaming_base import StreamingCallback


class StreamingSTTPipeline:
    """
    Coordinates incremental audio delivery to a streaming STT provider.

    Audio remains transient. The pipeline forwards chunks immediately
    and exposes provider transcription updates through a callback.
    """

    def __init__(
        self,
        stt,
        *,
        result_callback: StreamingCallback,
    ) -> None:
        if not callable(result_callback):
            raise TypeError("result_callback must be callable")

        self.stt = stt
        self.result_callback = result_callback

        self._lock = Lock()
        self._active = False
        self._token: CancellationToken | None = None

    @property
    def is_active(self) -> bool:
        return self._active

    @property
    def cancellation_token(self) -> CancellationToken | None:
        return self._token

    def start(self) -> None:
        with self._lock:
            if self._active:
                return

            self._token = CancellationToken()
            self._active = True

        self.stt.start()

    def push_audio(self, audio: bytes) -> None:
        with self._lock:
            if not self._active:
                raise RuntimeError("stream is not active")

            token = self._token

        if token is None:
            raise RuntimeError("stream cancellation token missing")

        token.throw_if_cancelled()

        self.stt.push_audio(audio)

    def finish(self) -> None:
        with self._lock:
            if not self._active:
                raise RuntimeError("stream is not active")

            token = self._token

        if token is None:
            raise RuntimeError("stream cancellation token missing")

        try:
            token.throw_if_cancelled()

            def handle_result(
                result: StreamingTranscriptionResult,
            ) -> None:
                token.throw_if_cancelled()
                self.result_callback(result)

            self.stt.finish(handle_result)

            token.throw_if_cancelled()

        finally:
            with self._lock:
                self._active = False
                self._token = None

    def cancel(self) -> None:
        with self._lock:
            token = self._token
            active = self._active

            self._active = False
            self._token = None

        if token is not None:
            token.cancel()

        if active:
            self.stt.cancel()
