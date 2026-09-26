import pytest

from sparks.voice.capture.base import (
    AudioCapture,
    AudioCaptureConfig,
)


def test_default_audio_capture_config() -> None:
    config = AudioCaptureConfig()

    assert config.sample_rate == 16_000
    assert config.channels == 1
    assert config.sample_width_bytes == 2
    assert config.block_size == 320


@pytest.mark.parametrize(
    "field,value",
    [
        ("sample_rate", 0),
        ("block_size", 0),
    ],
)
def test_audio_capture_config_rejects_non_positive_values(
    field: str,
    value: int,
) -> None:
    values = {
        "sample_rate": 16_000,
        "channels": 1,
        "sample_width_bytes": 2,
        "block_size": 320,
    }

    values[field] = value

    with pytest.raises(ValueError):
        AudioCaptureConfig(**values)


def test_audio_capture_config_requires_mono() -> None:
    with pytest.raises(ValueError):
        AudioCaptureConfig(channels=2)


def test_audio_capture_config_requires_16_bit_pcm() -> None:
    with pytest.raises(ValueError):
        AudioCaptureConfig(sample_width_bytes=4)


def test_audio_capture_is_abstract() -> None:
    with pytest.raises(TypeError):
        AudioCapture()
