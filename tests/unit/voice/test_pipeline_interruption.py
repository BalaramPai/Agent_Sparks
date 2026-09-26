from __future__ import annotations

import threading
import time

from sparks.voice.interruption import InterruptionReason
from sparks.voice.pipeline import VoicePipeline
from sparks.voice.types import VoiceState


class FakeCapture:
    def __init__(self):
        self.callback = None

    def start(self, callback):
        self.callback = callback

    def stop(self):
        pass

    def emit(self, audio: bytes):
        self.callback(audio)


class FakeVAD:
    def __init__(self, results):
        self.results = iter(results)

    def reset(self):
        pass

    def process(self, frame):
        return next(self.results)


class BlockingSTT:
    def __init__(self):
        self.started = threading.Event()
        self.release = threading.Event()
        self.cancel_called = False

    def transcribe(self, audio_chunks, callback):
        self.started.set()
        self.release.wait(timeout=5)

        callback(
            type(
                "Result",
                (),
                {
                    "result_type": __import__(
                        "sparks.voice.stt.types",
                        fromlist=["TranscriptionType"],
                    ).TranscriptionType.FINAL,
                    "text": "old response",
                    "confidence": 1.0,
                },
            )()
        )

    def cancel(self):
        self.cancel_called = True


def test_pipeline_exposes_interruption_controller():
    stt = BlockingSTT()

    pipeline = VoicePipeline(
        FakeCapture(),
        FakeVAD([None]),
        stt,
    )

    assert pipeline.interruption is not None
    assert pipeline.interruption.interrupted is False


def test_manual_interrupt_cancels_active_transcription():
    stt = BlockingSTT()
    capture = FakeCapture()

    pipeline = VoicePipeline(
        capture,
        FakeVAD([None, True, False]),
        stt,
        pre_roll_frames=0,
    )

    pipeline.start()

    capture.emit(b"speech")
    capture.emit(b"frame")
    capture.emit(b"stop")

    assert stt.started.wait(timeout=2)
    assert pipeline.state == VoiceState.TRANSCRIBING

    assert pipeline.interrupt(
        InterruptionReason.USER_SPEECH,
        source="test",
    ) is True

    assert stt.cancel_called is True
    assert pipeline.interruption.interrupted is True
    assert pipeline.interruption.last_event.reason == (
        InterruptionReason.USER_SPEECH
    )

    stt.release.set()

    deadline = time.monotonic() + 2

    while pipeline.state != VoiceState.LISTENING:
        if time.monotonic() >= deadline:
            break
        time.sleep(0.01)

    assert pipeline.state == VoiceState.LISTENING

    pipeline.stop()


def test_manual_interrupt_when_idle_returns_false():
    stt = BlockingSTT()

    pipeline = VoicePipeline(
        FakeCapture(),
        FakeVAD([None]),
        stt,
    )

    assert pipeline.interrupt() is False
    assert pipeline.interruption.interrupted is False


def test_start_resets_previous_interruption():
    stt = BlockingSTT()
    capture = FakeCapture()

    pipeline = VoicePipeline(
        capture,
        FakeVAD([None]),
        stt,
    )

    pipeline.start()

    pipeline.stop()

    pipeline.start()

    assert pipeline.interruption.interrupted is False
    assert pipeline.interruption.last_event is None

    pipeline.stop()
