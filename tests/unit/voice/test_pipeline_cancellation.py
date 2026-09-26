from __future__ import annotations

import threading
import time

from sparks.voice.cancellation import CancellationError
from sparks.voice.pipeline import VoicePipeline
from sparks.voice.types import VoiceEventType, VoiceState


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

    def emit(self, audio: bytes):
        assert self.callback is not None
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
                    "text": "should not survive cancellation",
                    "confidence": 1.0,
                },
            )()
        )

    def cancel(self):
        self.cancel_called = True


class FakeSTT:
    def __init__(self):
        self.cancel_called = False
        self.transcribed = []

    def transcribe(self, audio_chunks, callback):
        self.transcribed.append(tuple(audio_chunks))

    def cancel(self):
        self.cancel_called = True


def build_pipeline(stt, events=None):
    capture = FakeCapture()

    pipeline = VoicePipeline(
        capture,
        FakeVAD(
            [
                None,
                True,
                False,
            ]
        ),
        stt,
        pre_roll_frames=0,
        event_callback=events.append if events is not None else None,
    )

    return pipeline, capture


def test_transcription_gets_cancellation_token():
    stt = FakeSTT()
    pipeline, capture = build_pipeline(stt)

    pipeline.start()

    capture.emit(b"speech")
    capture.emit(b"frame")
    capture.emit(b"stop")

    deadline = time.monotonic() + 2

    while pipeline.cancellation_token is not None:
        if time.monotonic() >= deadline:
            break
        time.sleep(0.01)

    assert pipeline.cancellation_token is None
    assert pipeline.state == VoiceState.LISTENING

    pipeline.stop()


def test_cancel_transcription_calls_provider_cancel():
    stt = BlockingSTT()
    pipeline, capture = build_pipeline(stt)

    pipeline.start()

    capture.emit(b"speech")
    capture.emit(b"frame")
    capture.emit(b"stop")

    assert stt.started.wait(timeout=2)

    assert pipeline.is_transcribing is True
    assert pipeline.cancel_transcription() is True
    assert stt.cancel_called is True

    stt.release.set()

    deadline = time.monotonic() + 2

    while pipeline.state != VoiceState.LISTENING:
        if time.monotonic() >= deadline:
            break
        time.sleep(0.01)

    assert pipeline.state == VoiceState.LISTENING

    pipeline.stop()


def test_cancel_transcription_when_idle_returns_false():
    stt = FakeSTT()
    pipeline, _ = build_pipeline(stt)

    assert pipeline.cancel_transcription() is False


def test_cancelled_transcription_does_not_emit_completed_result():
    stt = BlockingSTT()
    events = []

    pipeline, capture = build_pipeline(
        stt,
        events,
    )

    pipeline.start()

    capture.emit(b"speech")
    capture.emit(b"frame")
    capture.emit(b"stop")

    assert stt.started.wait(timeout=2)

    assert pipeline.cancel_transcription() is True

    stt.release.set()

    deadline = time.monotonic() + 2

    while pipeline.state != VoiceState.LISTENING:
        if time.monotonic() >= deadline:
            break
        time.sleep(0.01)

    completed = [
        event
        for event in events
        if event.event_type == VoiceEventType.TRANSCRIPTION_COMPLETED
    ]

    assert completed == []

    pipeline.stop()


def test_stop_cancels_active_transcription():
    stt = BlockingSTT()
    pipeline, capture = build_pipeline(stt)

    pipeline.start()

    capture.emit(b"speech")
    capture.emit(b"frame")
    capture.emit(b"stop")

    assert stt.started.wait(timeout=2)

    pipeline.stop()

    assert stt.cancel_called is True
    assert pipeline.state == VoiceState.IDLE
    assert pipeline.is_running is False
    assert pipeline.cancellation_token is None

    stt.release.set()


def test_cancellation_token_throws_inside_pipeline_operation():
    from sparks.voice.cancellation import CancellationToken

    token = CancellationToken()

    assert token.is_cancelled is False

    token.cancel()

    assert token.is_cancelled is True

    try:
        token.throw_if_cancelled()
        assert False, "Expected CancellationError"
    except CancellationError:
        pass
