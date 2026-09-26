from sparks.voice.stt.types import (
    TranscriptionResult,
    TranscriptionType,
)


class TranscriptionAccumulator:
    """
    Maintains the current transcript for one voice turn.

    Partial results replace the currently visible transcript.
    A final result completes the turn and freezes the transcript.
    """

    def __init__(self) -> None:
        self._text = ""
        self._final = False

    @property
    def text(self) -> str:
        return self._text

    @property
    def is_final(self) -> bool:
        return self._final

    def update(self, result: TranscriptionResult) -> str:
        if self._final:
            return self._text

        self._text = result.text.strip()

        if result.result_type == TranscriptionType.FINAL:
            self._final = True

        return self._text

    def reset(self) -> None:
        self._text = ""
        self._final = False
