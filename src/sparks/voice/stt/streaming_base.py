from __future__ import annotations

from typing import Callable

from .streaming import StreamingTranscriptionResult

StreamingCallback = Callable[[StreamingTranscriptionResult], None]


class StreamingSpeechToText:
    def start(self) -> None:
        raise NotImplementedError

    def push_audio(self, audio: bytes) -> None:
        raise NotImplementedError

    def finish(self, callback: StreamingCallback) -> None:
        raise NotImplementedError

    def cancel(self) -> None:
        raise NotImplementedError
