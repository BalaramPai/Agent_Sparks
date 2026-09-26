from dataclasses import dataclass

import pytest

from sparks.voice.vad.base import (
    VoiceActivityDetector,
    VoiceActivityFrame,
)
from sparks.voice.vad.engine import (
    VadConfig,
    VadEngine,
    VadEventType,
)


def frame() -> VoiceActivityFrame:
    return VoiceActivityFrame(
        audio=b"\x00\x01" * 160,
        sample_rate=16_000,
        duration_ms=20,
    )


def test_voice_activity_frame_defaults() -> None:
    value = frame()

    assert value.sample_rate == 16_000
    assert value.duration_ms == 20
    assert value.audio


def test_voice_activity_frame_rejects_empty_audio() -> None:
    with pytest.raises(ValueError):
        VoiceActivityFrame(audio=b"")


@pytest.mark.parametrize("duration", [5, 15, 40])
def test_voice_activity_frame_rejects_invalid_duration(
    duration: int,
) -> None:
    with pytest.raises(ValueError):
        VoiceActivityFrame(
            audio=b"\x00\x01",
            duration_ms=duration,
        )


class FakeDetector(VoiceActivityDetector):
    def __init__(self, results: list[bool]) -> None:
        self.results = iter(results)

    def is_speech(self, frame: VoiceActivityFrame) -> bool:
        return next(self.results)


def test_vad_does_not_start_on_single_speech_frame() -> None:
    detector = FakeDetector([True])
    engine = VadEngine(
        detector,
        VadConfig(speech_start_frames=2),
    )

    assert engine.process(frame()) is None
    assert engine.is_speaking is False


def test_vad_starts_after_required_speech_frames() -> None:
    detector = FakeDetector([True, True])
    engine = VadEngine(
        detector,
        VadConfig(speech_start_frames=2),
    )

    assert engine.process(frame()) is None

    event = engine.process(frame())

    assert event is not None
    assert event.event_type == VadEventType.SPEECH_STARTED
    assert engine.is_speaking is True


def test_vad_does_not_stop_on_single_silence_frame() -> None:
    detector = FakeDetector(
        [True, True, False],
    )

    engine = VadEngine(
        detector,
        VadConfig(
            speech_start_frames=2,
            speech_stop_frames=2,
        ),
    )

    engine.process(frame())
    engine.process(frame())

    assert engine.process(frame()) is None
    assert engine.is_speaking is True


def test_vad_stops_after_required_silence_frames() -> None:
    detector = FakeDetector(
        [True, True, False, False],
    )

    engine = VadEngine(
        detector,
        VadConfig(
            speech_start_frames=2,
            speech_stop_frames=2,
        ),
    )

    engine.process(frame())
    engine.process(frame())

    assert engine.process(frame()) is None

    event = engine.process(frame())

    assert event is not None
    assert event.event_type == VadEventType.SPEECH_STOPPED
    assert engine.is_speaking is False


def test_vad_ignores_silence_before_speech() -> None:
    detector = FakeDetector([False, False, False])
    engine = VadEngine(detector)

    assert engine.process(frame()) is None
    assert engine.process(frame()) is None
    assert engine.process(frame()) is None

    assert engine.is_speaking is False


def test_vad_speech_resets_silence_counter() -> None:
    detector = FakeDetector(
        [True, True, False, True, False, False],
    )

    engine = VadEngine(
        detector,
        VadConfig(
            speech_start_frames=2,
            speech_stop_frames=2,
        ),
    )

    engine.process(frame())
    engine.process(frame())

    assert engine.is_speaking is True

    # One silence frame followed by speech must not stop the session.
    assert engine.process(frame()) is None
    assert engine.process(frame()) is None
    assert engine.is_speaking is True

    engine.process(frame())

    event = engine.process(frame())

    assert event is not None
    assert event.event_type == VadEventType.SPEECH_STOPPED


def test_vad_reset_returns_to_idle() -> None:
    detector = FakeDetector([True, True])
    engine = VadEngine(
        detector,
        VadConfig(speech_start_frames=2),
    )

    engine.process(frame())
    engine.process(frame())

    assert engine.is_speaking is True

    engine.reset()

    assert engine.is_speaking is False


def test_vad_config_rejects_invalid_values() -> None:
    with pytest.raises(ValueError):
        VadConfig(speech_start_frames=0)

    with pytest.raises(ValueError):
        VadConfig(speech_stop_frames=0)
