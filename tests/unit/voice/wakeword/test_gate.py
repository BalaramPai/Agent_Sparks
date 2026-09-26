from collections import deque

from sparks.voice.wakeword.base import WakeWordDetector
from sparks.voice.wakeword.gate import VoiceActivationGate
from sparks.voice.wakeword.policy import (
    ActivationConfig,
    ActivationPolicy,
    ActivationState,
)
from sparks.voice.wakeword.types import WakeWordDetection


class FakeWakeWordDetector(WakeWordDetector):
    def __init__(self, detections):
        self.detections = deque(detections)
        self.reset_called = False

    def detect(self, audio: bytes) -> WakeWordDetection:
        return self.detections.popleft()

    def reset(self) -> None:
        self.reset_called = True


def inactive_detection():
    return WakeWordDetection(detected=False)


def active_detection():
    return WakeWordDetection(
        detected=True,
        keyword="sparks",
        confidence=0.95,
    )


def test_gate_starts_inactive():
    detector = FakeWakeWordDetector([])
    policy = ActivationPolicy()

    gate = VoiceActivationGate(
        detector,
        policy,
    )

    assert not gate.is_active


def test_gate_activates_when_wake_word_is_detected():
    detector = FakeWakeWordDetector([
        active_detection(),
    ])

    policy = ActivationPolicy(
        ActivationConfig(
            activation_timeout_frames=3,
        )
    )

    gate = VoiceActivationGate(
        detector,
        policy,
    )

    event = gate.process(b"audio")

    assert event is not None
    assert event.state == ActivationState.ACTIVE
    assert event.keyword == "sparks"
    assert gate.is_active


def test_gate_remains_inactive_without_wake_word():
    detector = FakeWakeWordDetector([
        inactive_detection(),
    ])

    policy = ActivationPolicy()

    gate = VoiceActivationGate(
        detector,
        policy,
    )

    event = gate.process(b"audio")

    assert event is None
    assert not gate.is_active


def test_gate_expires_activation():
    detector = FakeWakeWordDetector([
        active_detection(),
        inactive_detection(),
        inactive_detection(),
    ])

    policy = ActivationPolicy(
        ActivationConfig(
            activation_timeout_frames=2,
        )
    )

    gate = VoiceActivationGate(
        detector,
        policy,
    )

    gate.process(b"wake")

    assert gate.is_active

    assert gate.process(b"audio") is None
    assert gate.is_active

    event = gate.process(b"audio")

    assert event is not None
    assert event.state == ActivationState.INACTIVE
    assert not gate.is_active


def test_gate_emits_events_through_callback():
    detector = FakeWakeWordDetector([
        active_detection(),
    ])

    policy = ActivationPolicy(
        ActivationConfig(
            activation_timeout_frames=3,
        )
    )

    events = []

    gate = VoiceActivationGate(
        detector,
        policy,
        event_callback=events.append,
    )

    gate.process(b"audio")

    assert len(events) == 1
    assert events[0].state == ActivationState.ACTIVE
    assert events[0].keyword == "sparks"


def test_gate_manual_deactivation():
    detector = FakeWakeWordDetector([
        active_detection(),
    ])

    policy = ActivationPolicy(
        ActivationConfig(
            activation_timeout_frames=10,
        )
    )

    gate = VoiceActivationGate(
        detector,
        policy,
    )

    gate.process(b"wake")

    event = gate.deactivate()

    assert event is not None
    assert event.state == ActivationState.INACTIVE
    assert not gate.is_active


def test_gate_reset_resets_detector_and_policy():
    detector = FakeWakeWordDetector([
        active_detection(),
    ])

    policy = ActivationPolicy(
        ActivationConfig(
            activation_timeout_frames=10,
        )
    )

    gate = VoiceActivationGate(
        detector,
        policy,
    )

    gate.process(b"wake")

    assert gate.is_active

    gate.reset()

    assert not gate.is_active
    assert detector.reset_called


def test_gate_can_bypass_wake_word_when_disabled():
    detector = FakeWakeWordDetector([
        inactive_detection(),
    ])

    policy = ActivationPolicy(
        ActivationConfig(
            enabled=False,
        )
    )

    gate = VoiceActivationGate(
        detector,
        policy,
    )

    assert gate.is_active

    assert gate.process(b"audio") is None
    assert gate.is_active
