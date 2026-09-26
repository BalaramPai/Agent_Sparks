from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable

from sparks.voice.stt.types import TranscriptionResult


TranscriptionCallback = Callable[[TranscriptionResult], None]


class SpeechToText(ABC):
    """
    Provider-independent speech-to-text contract.

    Audio arrives as transient PCM bytes. The STT provider emits
    transcription updates through the supplied callback.

    The interface intentionally does not expose a specific
    model, runtime, device, or vendor.
    """

    @abstractmethod
    def transcribe(
        self,
        audio_chunks: Iterable[bytes],
        callback: TranscriptionCallback,
    ) -> None:
        """
        Transcribe an utterance from audio chunks.

        Providers may emit zero or more PARTIAL results followed
        by a FINAL result.
        """
        raise NotImplementedError

    @abstractmethod
    def cancel(self) -> None:
        """
        Cancel an active transcription operation.
        """
        raise NotImplementedError
