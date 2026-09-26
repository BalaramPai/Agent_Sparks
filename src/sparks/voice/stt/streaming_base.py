from __future__ import annotations

from collections.abc import Callable, Iterable

from sparks.voice.stt.streaming import (
    StreamingTranscriptionResult,
    StreamingTranscriptionType,
)


StreamingCallback = Callable[
    [StreamingTranscriptionResult],
    None,
]


class StreamingSpeechToText:
    """
    Provider-independent streaming STT contract.

    Implementations consume incremental PCM audio chunks and may
    emit zero or more PARTIAL results followed by a FINAL result.

    The contract intentionally does not require a specific STT
    provider or inference runtime.
    """

    def start(self) -> None:
        raise NotImplementedError

    def push_audio(self, audio: bytes) -> None:
        raise NotImplementedError

    def finish(
        self,
        callback: StreamingCallback,
    ) -> None:
        raise NotImplementedError

    def cancel(self) -> None:
        raise NotImplementedError
