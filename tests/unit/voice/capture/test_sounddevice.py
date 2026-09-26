from unittest.mock import MagicMock, patch

import pytest

from sparks.voice.capture.base import AudioCaptureConfig
from sparks.voice.capture.sounddevice import SoundDeviceCapture


def test_capture_starts_and_forwards_audio() -> None:
    callback = MagicMock()
    fake_stream = MagicMock()

    with patch(
        "sparks.voice.capture.sounddevice.sd.RawInputStream",
        return_value=fake_stream,
    ) as stream_factory:
        capture = SoundDeviceCapture(
            AudioCaptureConfig(
                sample_rate=16_000,
                channels=1,
                sample_width_bytes=2,
                block_size=320,
            )
        )

        capture.start(callback)

        assert capture.is_running is True

        stream_factory.assert_called_once_with(
            samplerate=16_000,
            blocksize=320,
            device=None,
            channels=1,
            dtype="int16",
            callback=capture._handle_audio,
        )

        fake_stream.start.assert_called_once()


def test_audio_callback_forwards_bytes() -> None:
    callback = MagicMock()

    capture = SoundDeviceCapture()

    capture._callback = callback
    capture._running = True

    audio = bytearray(b"\x01\x02\x03\x04")

    capture._handle_audio(
        audio,
        frames=2,
        time=None,
        status=None,
    )

    callback.assert_called_once_with(bytes(audio))


def test_capture_stop_closes_stream() -> None:
    callback = MagicMock()
    fake_stream = MagicMock()

    with patch(
        "sparks.voice.capture.sounddevice.sd.RawInputStream",
        return_value=fake_stream,
    ):
        capture = SoundDeviceCapture()
        capture.start(callback)

        capture.stop()

        fake_stream.stop.assert_called_once()
        fake_stream.close.assert_called_once()

        assert capture.is_running is False


def test_capture_start_requires_callable_callback() -> None:
    capture = SoundDeviceCapture()

    with pytest.raises(TypeError):
        capture.start(None)


def test_capture_start_is_idempotent() -> None:
    callback = MagicMock()
    fake_stream = MagicMock()

    with patch(
        "sparks.voice.capture.sounddevice.sd.RawInputStream",
        return_value=fake_stream,
    ) as stream_factory:
        capture = SoundDeviceCapture()

        capture.start(callback)
        capture.start(callback)

        stream_factory.assert_called_once()
        fake_stream.start.assert_called_once()


def test_capture_start_cleans_up_when_stream_creation_fails() -> None:
    callback = MagicMock()

    with patch(
        "sparks.voice.capture.sounddevice.sd.RawInputStream",
        side_effect=RuntimeError("audio device unavailable"),
    ):
        capture = SoundDeviceCapture()

        with pytest.raises(RuntimeError):
            capture.start(callback)

        assert capture.is_running is False
        assert capture._stream is None
        assert capture._callback is None
