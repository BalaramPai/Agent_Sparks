from __future__ import annotations

import time

from sparks.voice.pipeline import VoicePipeline
from sparks.voice.types import VoiceEventType, VoiceState


class FakeCapture:
    def __init__(self):
        self.callback = None
        self.started = False

    def start(self, callback):
        self.callback = callback
        self.started = True

    def stop(self):
        self.started = False

    def emit(self, audio: bytes):
        assert self.callback is not None
        self.callback(audio)


class FakeVAD:
    def __init__(self, results):
        self.results = iter(results)

    def reset(self):
        pass

    def process(self, frame):
        return next(self.results, None)


class FakeSTT:
    def cancel(self):
        pass

    def transcribe(self, audio_chunks, callback):
        from sparks.voice.stt.types import (
            TranscriptionResult,
            TranscriptionType,
        )

        callback(
            TranscriptionResult(
                text="legacy",
                result_type=TranscriptionType.FINAL,
                confidence=0.9,
                language="en",
            )
        )


class FakeStreamingSTT:
    def __init__(self):
        self.audio = []
        self.started = False
        self.finished = False
        self.cancelled = False

    def start(self):
        self.started = True

    def push_audio(self, audio):
        self.audio.append(audio)

    def finish(self, callback):
        self.finished = True

        from sparks.voice.stt.streaming import (
            StreamingTranscriptionResult,
            StreamingTranscriptionType,
        )

        callback(
            StreamingTranscriptionResult(
                text="open",
                result_type=StreamingTranscriptionType.PARTIAL,
                confidence=0.9,
                language="en",
                sequence=1,
            )
        )

        callback(
            StreamingTranscriptionResult(
                text="open chrome",
                result_type=StreamingTranscriptionType.FINAL,
                confidence=0.95,
                language="en",
                sequence=2,
            )
        )

    def cancel(self):
        self.cancelled = True


def build_pipeline(events):
    capture = FakeCapture()

    # First frame = pre-roll
    # Second frame = speech start
    # Third frame = speech continues
    # Fourth frame = speech stop
    vad = FakeVAD(
        [
            None,
            True,
            None,
            False,
        ]
    )

    streaming = FakeStreamingSTT()

    pipeline = VoicePipeline(
        capture,
        vad,
        FakeSTT(),
        streaming_stt=streaming,
        pre_roll_frames=1,
        event_callback=events.append,
    )

    return pipeline, capture


def test_pipeline_can_use_streaming_stt():
    events = []

    pipeline, capture = build_pipeline(events)

    pipeline.start()

    capture.emit(b"hello")
    capture.emit(b"world")

    assert pipeline.is_streaming is True
    assert pipeline.state == VoiceState.TRANSCRIBING

    capture.emit(b"more")
    capture.emit(b"stop")

    assert pipeline.is_streaming is False
    assert pipeline.state == VoiceState.LISTENING

    streaming_results = [
        event
        for event in events
        if event.metadata.get("streaming") is True
        and event.event_type
        in (
            VoiceEventType.TRANSCRIPTION_PARTIAL,
            VoiceEventType.TRANSCRIPTION_COMPLETED,
        )
    ]

    assert len(streaming_results) == 2

    assert streaming_results[0].event_type == (
        VoiceEventType.TRANSCRIPTION_PARTIAL
    )

    assert streaming_results[0].text == "open"

    assert streaming_results[1].event_type == (
        VoiceEventType.TRANSCRIPTION_COMPLETED
    )

    assert streaming_results[1].text == "open chrome"

    pipeline.stop()


def test_streaming_pipeline_forwards_audio():
    events = []

    pipeline, capture = build_pipeline(events)

    pipeline.start()

    # First frame is captured as pre-roll.
    capture.emit(b"first")

    # Speech starts here. The pipeline forwards the accumulated
    # utterance, including pre-roll, into streaming STT.
    capture.emit(b"second")

    # Speech continues.
    capture.emit(b"third")

    streaming = pipeline.streaming_stt

    assert streaming.audio == [
        b"first",
        b"second",
        b"third",
    ]

    pipeline.stop()


def test_streaming_pipeline_emits_transcription_started():
    events = []

    pipeline, capture = build_pipeline(events)

    pipeline.start()

    # First frame is pre-roll.
    capture.emit(b"pre")

    # This frame triggers speech start.
    capture.emit(b"start")

    started = [
        event
        for event in events
        if event.event_type
        == VoiceEventType.TRANSCRIPTION_STARTED
    ]

    assert len(started) == 1
    assert started[0].metadata["streaming"] is True

    pipeline.stop()


def test_pipeline_without_streaming_stt_keeps_legacy_path():
    events = []

    capture = FakeCapture()

    class LegacySTT(FakeSTT):
        def transcribe(self, audio_chunks, callback):
            from sparks.voice.stt.types import (
                TranscriptionResult,
                TranscriptionType,
            )

            callback(
                TranscriptionResult(
                    text="legacy result",
                    result_type=TranscriptionType.FINAL,
                    confidence=0.9,
                    language="en",
                )
            )

    pipeline = VoicePipeline(
        capture,
        FakeVAD(
            [
                None,
                True,
                False,
            ]
        ),
        LegacySTT(),
        streaming_stt=None,
        pre_roll_frames=0,
        event_callback=events.append,
    )

    pipeline.start()

    # None -> no speech
    capture.emit(b"pre")

    # True -> speech started
    capture.emit(b"speech")

    # False -> speech stopped
    capture.emit(b"stop")

    deadline = time.monotonic() + 2

    while pipeline.state != VoiceState.LISTENING:
        if time.monotonic() >= deadline:
            break

        time.sleep(0.01)

    completed = [
        event
        for event in events
        if event.event_type
        == VoiceEventType.TRANSCRIPTION_COMPLETED
    ]

    assert len(completed) == 1
    assert completed[0].text == "legacy result"

    pipeline.stop()