from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from sparks.voice.stt.faster_whisper import FasterWhisperSTT
from sparks.voice.stt.types import TranscriptionType


def test_default_configuration() -> None:
    stt = FasterWhisperSTT()

    assert stt.model_size == "base"
    assert stt.device == "cpu"
    assert stt.compute_type == "int8"
    assert stt.language is None
    assert stt.beam_size == 1
    assert stt.is_loaded is False


@pytest.mark.parametrize(
    "kwargs",
    [
        {"model_size": ""},
        {"device": "metal"},
        {"compute_type": "invalid"},
        {"beam_size": 0},
    ],
)
def test_invalid_configuration_is_rejected(kwargs: dict) -> None:
    with pytest.raises(ValueError):
        FasterWhisperSTT(**kwargs)


def test_load_creates_whisper_model() -> None:
    fake_model = MagicMock()

    with patch(
        "sparks.voice.stt.faster_whisper.WhisperModel",
        return_value=fake_model,
    ) as model_factory:
        stt = FasterWhisperSTT(
            model_size="tiny",
            device="cpu",
            compute_type="int8",
        )

        stt.load()

        model_factory.assert_called_once_with(
            "tiny",
            device="cpu",
            compute_type="int8",
        )

        assert stt.is_loaded is True


def test_load_is_idempotent() -> None:
    fake_model = MagicMock()

    with patch(
        "sparks.voice.stt.faster_whisper.WhisperModel",
        return_value=fake_model,
    ) as model_factory:
        stt = FasterWhisperSTT()

        stt.load()
        stt.load()

        model_factory.assert_called_once()


def test_transcribe_converts_pcm_to_float32_audio() -> None:
    fake_model = MagicMock()

    segments = [
        SimpleNamespace(
            text=" open chrome ",
            avg_logprob=-0.1,
        ),
        SimpleNamespace(
            text="",
            avg_logprob=-0.2,
        ),
        SimpleNamespace(
            text=" and open youtube ",
            avg_logprob=-0.2,
        ),
    ]

    fake_model.transcribe.return_value = (
        iter(segments),
        SimpleNamespace(
            language="en",
        ),
    )

    stt = FasterWhisperSTT()
    stt._model = fake_model

    results = []

    stt.transcribe(
        [b"\x00\x00\x00\x40", b"\x00\xc0"],
        results.append,
    )

    assert len(results) == 2

    assert results[0].text == "open chrome"
    assert results[0].result_type == TranscriptionType.FINAL
    assert results[0].language == "en"

    assert results[1].text == "and open youtube"
    assert results[1].result_type == TranscriptionType.FINAL

    fake_model.transcribe.assert_called_once()

    call_args, call_kwargs = fake_model.transcribe.call_args

    audio = call_args[0]

    assert isinstance(audio, np.ndarray)
    assert audio.dtype == np.float32
    assert audio.shape == (3,)

    expected = np.array(
        [
            0.0,
            16384 / 32768,
            -16384 / 32768,
        ],
        dtype=np.float32,
    )

    np.testing.assert_allclose(audio, expected)

    assert call_kwargs["language"] is None
    assert call_kwargs["beam_size"] == 1
    assert call_kwargs["vad_filter"] is False
    assert call_kwargs["condition_on_previous_text"] is False


def test_transcribe_loads_model_when_needed() -> None:
    fake_model = MagicMock()

    fake_model.transcribe.return_value = (
        iter([]),
        SimpleNamespace(language="en"),
    )

    with patch(
        "sparks.voice.stt.faster_whisper.WhisperModel",
        return_value=fake_model,
    ):
        stt = FasterWhisperSTT()

        stt.transcribe([b"\x00\x01"], lambda result: None)

        assert stt.is_loaded is True


def test_transcribe_rejects_non_callable_callback() -> None:
    stt = FasterWhisperSTT()

    with pytest.raises(TypeError):
        stt.transcribe([b"\x00"], None)


def test_transcribe_ignores_empty_audio() -> None:
    fake_model = MagicMock()

    stt = FasterWhisperSTT()
    stt._model = fake_model

    callback = MagicMock()

    stt.transcribe([], callback)

    fake_model.transcribe.assert_not_called()
    callback.assert_not_called()


def test_cancel_stops_segment_processing() -> None:
    fake_model = MagicMock()

    segments = [
        SimpleNamespace(
            text="first",
            avg_logprob=-0.1,
        ),
        SimpleNamespace(
            text="second",
            avg_logprob=-0.1,
        ),
    ]

    def segment_generator():
        yield segments[0]
        stt.cancel()
        yield segments[1]

    fake_model.transcribe.return_value = (
        segment_generator(),
        SimpleNamespace(language="en"),
    )

    stt = FasterWhisperSTT()
    stt._model = fake_model

    callback = MagicMock()

    stt.transcribe([b"\x00\x01"], callback)

    callback.assert_called_once()


def test_cancel_before_transcription_resets_for_new_turn() -> None:
    fake_model = MagicMock()

    fake_model.transcribe.return_value = (
        iter(
            [
                SimpleNamespace(
                    text="hello",
                    avg_logprob=-0.1,
                )
            ]
        ),
        SimpleNamespace(language="en"),
    )

    stt = FasterWhisperSTT()
    stt._model = fake_model

    stt.cancel()

    callback = MagicMock()

    stt.transcribe([b"\x00\x01"], callback)

    callback.assert_called_once()


def test_confidence_is_clamped() -> None:
    segment = SimpleNamespace(avg_logprob=0.0)

    confidence = FasterWhisperSTT._segment_confidence(segment)

    assert confidence == 1.0


def test_missing_confidence_returns_none() -> None:
    segment = SimpleNamespace()

    confidence = FasterWhisperSTT._segment_confidence(segment)

    assert confidence is None
