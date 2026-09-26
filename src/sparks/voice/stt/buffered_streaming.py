from __future__ import annotations

from sparks.voice.stt.streaming import (
    StreamingTranscriptionResult,
    StreamingTranscriptionType,
)
from sparks.voice.stt.streaming_base import (
    StreamingCallback,
    StreamingSpeechToText,
)


class BufferedStreamingSTT(StreamingSpeechToText):
    """
    Reference streaming adapter.

    It accepts audio incrementally but defers provider transcription
    until finish(). This gives SPARKS a streaming-compatible lifecycle
    without falsely claiming that the underlying provider is already
    producing real-time partial hypotheses.
    """

    def __init__(self, provider) -> None:
        self.provider = provider
        self._chunks: list[bytes] = []
        self._active = False
        self._cancelled = False
        self._sequence = 0

    @property
    def is_active(self) -> bool:
        return self._active

    def start(self) -> None:
        self._chunks.clear()
        self._active = True
        self._cancelled = False
        self._sequence = 0

    def push_audio(self, audio: bytes) -> None:
        if not self._active:
            raise RuntimeError("stream has not been started")

        if self._cancelled:
            return

        if audio:
            self._chunks.append(audio)

    def finish(
        self,
        callback: StreamingCallback,
    ) -> None:
        if not self._active:
            raise RuntimeError("stream has not been started")

        try:
            if self._cancelled:
                return

            def handle_result(result) -> None:
                if self._cancelled:
                    return

                self._sequence += 1

                callback(
                    StreamingTranscriptionResult(
                        text=result.text,
                        result_type=(
                            StreamingTranscriptionType.FINAL
                        ),
                        confidence=result.confidence,
                        language=result.language,
                        sequence=self._sequence,
                    )
                )

            self.provider.transcribe(
                tuple(self._chunks),
                callback=handle_result,
            )

        finally:
            self._active = False

    def cancel(self) -> None:
        self._cancelled = True

        cancel = getattr(self.provider, "cancel", None)

        if callable(cancel):
            cancel()
