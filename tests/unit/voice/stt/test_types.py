import pytest

from sparks.voice.stt.accumulator import TranscriptionAccumulator
from sparks.voice.stt.base import SpeechToText
from sparks.voice.stt.types import (
    TranscriptionResult,
    TranscriptionType,
)


def test_partial_transcription_result() -> None:
    result = TranscriptionResult(
        text="hello wor",
        result_type=TranscriptionType.PARTIAL,
        confidence=0.91,
        language="en",
    )

    assert result.text == "hello wor"
    assert result.is_partial is True
    assert result.is_final is False
    assert result.confidence == 0.91
    assert result.language == "en"


def test_final_transcription_result() -> None:
    result = TranscriptionResult(
        text="hello world",
        result_type=TranscriptionType.FINAL,
    )

    assert result.text == "hello world"
    assert result.is_partial is False
    assert result.is_final is True


def test_empty_transcription_is_rejected() -> None:
    with pytest.raises(ValueError):
        TranscriptionResult(
            text="   ",
            result_type=TranscriptionType.FINAL,
        )


@pytest.mark.parametrize("confidence", [-0.1, 1.1])
def test_invalid_confidence_is_rejected(
    confidence: float,
) -> None:
    with pytest.raises(ValueError):
        TranscriptionResult(
            text="hello",
            result_type=TranscriptionType.PARTIAL,
            confidence=confidence,
        )


def test_speech_to_text_is_abstract() -> None:
    with pytest.raises(TypeError):
        SpeechToText()


def test_accumulator_starts_empty() -> None:
    accumulator = TranscriptionAccumulator()

    assert accumulator.text == ""
    assert accumulator.is_final is False


def test_accumulator_replaces_partial_transcript() -> None:
    accumulator = TranscriptionAccumulator()

    accumulator.update(
        TranscriptionResult(
            text="open",
            result_type=TranscriptionType.PARTIAL,
        )
    )

    assert accumulator.text == "open"

    accumulator.update(
        TranscriptionResult(
            text="open chrome",
            result_type=TranscriptionType.PARTIAL,
        )
    )

    assert accumulator.text == "open chrome"
    assert accumulator.is_final is False


def test_accumulator_freezes_after_final_result() -> None:
    accumulator = TranscriptionAccumulator()

    accumulator.update(
        TranscriptionResult(
            text="open chrome",
            result_type=TranscriptionType.PARTIAL,
        )
    )

    accumulator.update(
        TranscriptionResult(
            text="open Chrome",
            result_type=TranscriptionType.FINAL,
        )
    )

    assert accumulator.text == "open Chrome"
    assert accumulator.is_final is True

    # A provider must not be able to mutate a completed turn.
    accumulator.update(
        TranscriptionResult(
            text="something else",
            result_type=TranscriptionType.PARTIAL,
        )
    )

    assert accumulator.text == "open Chrome"
    assert accumulator.is_final is True


def test_accumulator_reset_starts_new_turn() -> None:
    accumulator = TranscriptionAccumulator()

    accumulator.update(
        TranscriptionResult(
            text="open Chrome",
            result_type=TranscriptionType.FINAL,
        )
    )

    accumulator.reset()

    assert accumulator.text == ""
    assert accumulator.is_final is False


def test_transcription_result_is_immutable() -> None:
    result = TranscriptionResult(
        text="hello",
        result_type=TranscriptionType.FINAL,
    )

    with pytest.raises(AttributeError):
        result.text = "changed"
