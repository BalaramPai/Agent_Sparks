from collections import deque
from threading import Event
from time import sleep

from sparks.voice.pipeline import VoicePipeline
from sparks.voice.types import VoiceEventType, VoiceState
from sparks.voice.wakeword.base import WakeWordDetector
from sparks.voice.wakeword.gate import VoiceActivationGate
from sparks.voice.wakeword.policy import (
    ActivationConfig,
    ActivationPolicy,
)
from sparks.voice.wakeword.types import WakeWordDetection


class FakeCapture:
    def __init__(self):
        self.callback = None
        self.started = False
        self.stopped = False

    def start(self, callback):
        self.callback = callback
        self.started = True

    def stop(self):
        self.stopped = True

    def push(self, audio: bytes):
        assert self.callback is not None
        self.callback(audio)


class FakeVAD:
    def __init__(self, events):
        self.events = deque(events)
        self.reset_count = 0

    def reset(self):
        self.reset_count += 1

    def process(self, frame):
        if self.events:
            return self.events.popleft()
        return None


class FakeSTT:
    def __init__(self):
        self.calls = []
        self.cancelled = False
        self.started = Event()
        self.release = Event()

    def transcribe(self, audio_chunks, callback):
        self.calls.append(tuple(audio_chunks))
        self.started.set()

        callback(
            type(
                "Result",
                (),
                {
                    "text": "hello sparks",
                    "result_type": "final",
                    "confidence": 0.9,
                },
            )()
        )

    def cancel(self):
        self.cancelled = True


class FakeWakeWordDetector(WakeWordDetector):
    def __init__(self, detections):
        self.detections = deque(detections)
        self.reset_count = 0

    def detect(self, audio: bytes):
        if self.detections:
            return self.detections.popleft()

        return WakeWordDetection(detected=False)

    def reset(self):
        self.reset_count += 1


class FakeVadEvent:
    def __init__(self, event_type):
        self.type = event_type


def make_gate(detections):
    detector = FakeWakeWordDetector(detections)

    policy = ActivationPolicy(
        ActivationConfig(
            activation_timeout_frames=20,
        )
    )

    return VoiceActivationGate(
        detector,
        policy,
    ), detector


def test_pipeline_does_not_transcribe_without_activation():
    capture = FakeCapture()

    vad = FakeVAD([
        FakeVadEvent("speech_started"),
        FakeVadEvent("speech_stopped"),
    ])

    stt = FakeSTT()

    gate, _ = make_gate([
        WakeWordDetection(detected=False),
        WakeWordDetection(detected=False),
    ])

    pipeline = VoicePipeline(
        capture,
        vad,
        stt,
        activation_gate=gate,
    )

    pipeline.start()

    capture.push(b"speech-start")
    capture.push(b"speech-stop")

    sleep(0.05)

    assert stt.calls == []


def test_pipeline_transcribes_after_wake_word_activation():
    capture = FakeCapture()

    vad = FakeVAD([
        FakeVadEvent("speech_started"),
        None,
        FakeVadEvent("speech_stopped"),
    ])

    stt = FakeSTT()

    gate, _ = make_gate([
        WakeWordDetection(
            detected=True,
            keyword="sparks",
            confidence=0.95,
        ),
        WakeWordDetection(detected=False),
        WakeWordDetection(detected=False),
    ])

    pipeline = VoicePipeline(
        capture,
        vad,
        stt,
        activation_gate=gate,
    )

    pipeline.start()

    capture.push(b"wake")
    capture.push(b"hello")
    capture.push(b"stop")

    assert stt.started.wait(timeout=1)

    assert len(stt.calls) == 1
    assert stt.calls[0] == (
        b"wake",
        b"hello",
        b"stop",
    )


def test_pipeline_captures_pre_roll_for_authorized_utterance():
    capture = FakeCapture()

    vad = FakeVAD([
        None,
        FakeVadEvent("speech_started"),
        None,
        FakeVadEvent("speech_stopped"),
    ])

    stt = FakeSTT()

    gate, _ = make_gate([
        WakeWordDetection(
            detected=True,
            keyword="sparks",
            confidence=0.95,
        ),
        WakeWordDetection(detected=False),
        WakeWordDetection(detected=False),
    ])

    pipeline = VoicePipeline(
        capture,
        vad,
        stt,
        activation_gate=gate,
        pre_roll_frames=2,
    )

    pipeline.start()

    capture.push(b"wake")
    capture.push(b"pre-roll")
    capture.push(b"speech")
    capture.push(b"stop")

    assert stt.started.wait(timeout=1)

    assert stt.calls[0] == (
        b"wake",
        b"pre-roll",
        b"speech",
        b"stop",
    )


def test_pipeline_activation_is_snapshotted_at_speech_start():
    capture = FakeCapture()

    vad = FakeVAD([
        FakeVadEvent("speech_started"),
        None,
        FakeVadEvent("speech_stopped"),
    ])

    stt = FakeSTT()

    gate, _ = make_gate([
        WakeWordDetection(
            detected=True,
            keyword="sparks",
            confidence=0.95,
        ),
        WakeWordDetection(detected=False),
        WakeWordDetection(detected=False),
    ])

    pipeline = VoicePipeline(
        capture,
        vad,
        stt,
        activation_gate=gate,
    )

    pipeline.start()

    capture.push(b"wake")
    capture.push(b"speech")
    capture.push(b"stop")

    assert stt.started.wait(timeout=1)
    assert len(stt.calls) == 1


def test_pipeline_without_activation_gate_remains_compatible():
    capture = FakeCapture()

    vad = FakeVAD([
        FakeVadEvent("speech_started"),
        FakeVadEvent("speech_stopped"),
    ])

    stt = FakeSTT()

    pipeline = VoicePipeline(
        capture,
        vad,
        stt,
        activation_gate=None,
    )

    pipeline.start()

    capture.push(b"speech")
    capture.push(b"stop")

    assert stt.started.wait(timeout=1)
    assert len(stt.calls) == 1


def test_pipeline_resets_activation_gate_on_stop():
    capture = FakeCapture()

    vad = FakeVAD([])

    stt = FakeSTT()

    gate, detector = make_gate([
        WakeWordDetection(
            detected=True,
            keyword="sparks",
            confidence=0.95,
        ),
    ])

    pipeline = VoicePipeline(
        capture,
        vad,
        stt,
        activation_gate=gate,
    )

    pipeline.start()

    capture.push(b"wake")

    assert gate.is_active

    pipeline.stop()

    assert not gate.is_active
    assert detector.reset_count >= 1
    assert pipeline.state == VoiceState.IDLE


def test_pipeline_start_is_idempotent_with_activation_gate():
    capture = FakeCapture()
    vad = FakeVAD([])
    stt = FakeSTT()

    gate, _ = make_gate([])

    pipeline = VoicePipeline(
        capture,
        vad,
        stt,
        activation_gate=gate,
    )

    pipeline.start()
    pipeline.start()

    assert pipeline.is_running
    assert pipeline.state == VoiceState.LISTENING

    pipeline.stop()


def test_pipeline_emits_authorization_metadata():
    capture = FakeCapture()

    events = []

    vad = FakeVAD([
        FakeVadEvent("speech_started"),
        FakeVadEvent("speech_stopped"),
    ])

    stt = FakeSTT()

    gate, _ = make_gate([
        WakeWordDetection(
            detected=True,
            keyword="sparks",
            confidence=0.95,
        ),
    ])

    pipeline = VoicePipeline(
        capture,
        vad,
        stt,
        activation_gate=gate,
        event_callback=events.append,
    )

    pipeline.start()

    capture.push(b"wake")
    capture.push(b"speech")

    assert any(
        event.event_type == VoiceEventType.SPEECH_STARTED
        and event.metadata["activated"] is True
        for event in events
    )

    pipeline.stop()


