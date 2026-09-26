from __future__ import annotations

from sparks.voice.stt.streaming import (
    StreamingTranscriptionResult,
    StreamingTranscriptionType,
)
from sparks.voice.stt.streaming_pipeline import StreamingSTTPipeline


class FakeStreamingSTT:
    def __init__(self):
        self.started = False
        self.audio = []
        self.cancelled = False

    def start(self):
        self.started = True
        self.audio.clear()
        self.cancelled = False

    def push_audio(self, audio):
        if self.cancelled:
            return

        self.audio.append(audio)

    def finish(self, callback):
        if self.cancelled:
            return

        callback(
            StreamingTranscriptionResult(
                text="hello",
                result_type=StreamingTranscriptionType.PARTIAL,
                confidence=0.8,
                language="en",
                sequence=1,
            )
        )

        callback(
            StreamingTranscriptionResult(
                text="hello sparks",
                result_type=StreamingTranscriptionType.FINAL,
                confidence=0.95,
                language="en",
                sequence=2,
            )
        )

    def cancel(self):
        self.cancelled = True


def test_streaming_pipeline_starts_provider():
    provider = FakeStreamingSTT()
    results = []

    pipeline = StreamingSTTPipeline(
        provider,
        result_callback=results.append,
    )

    pipeline.start()

    assert pipeline.is_active is True
    assert provider.started is True


def test_streaming_pipeline_forwards_audio():
    provider = FakeStreamingSTT()
    results = []

    pipeline = StreamingSTTPipeline(
        provider,
        result_callback=results.append,
    )

    pipeline.start()

    pipeline.push_audio(b"a")
    pipeline.push_audio(b"b")
    pipeline.push_audio(b"c")

    assert provider.audio == [b"a", b"b", b"c"]


def test_streaming_pipeline_receives_partial_and_final():
    provider = FakeStreamingSTT()
    results = []

    pipeline = StreamingSTTPipeline(
        provider,
        result_callback=results.append,
    )

    pipeline.start()
    pipeline.push_audio(b"audio")
    pipeline.finish()

    assert len(results) == 2

    assert results[0].result_type == (
        StreamingTranscriptionType.PARTIAL
    )
    assert results[0].text == "hello"

    assert results[1].result_type == (
        StreamingTranscriptionType.FINAL
    )
    assert results[1].text == "hello sparks"

    assert pipeline.is_active is False


def test_streaming_pipeline_rejects_audio_before_start():
    provider = FakeStreamingSTT()
    pipeline = StreamingSTTPipeline(
        provider,
        result_callback=lambda result: None,
    )

    try:
        pipeline.push_audio(b"audio")
        assert False, "Expected RuntimeError"
    except RuntimeError:
        pass


def test_streaming_pipeline_cancellation():
    provider = FakeStreamingSTT()
    pipeline = StreamingSTTPipeline(
        provider,
        result_callback=lambda result: None,
    )

    pipeline.start()

    assert pipeline.cancellation_token is not None
    assert pipeline.cancellation_token.is_cancelled is False

    pipeline.cancel()

    assert provider.cancelled is True
    assert pipeline.is_active is False
    assert pipeline.cancellation_token is None


def test_streaming_pipeline_can_restart():
    provider = FakeStreamingSTT()
    results = []

    pipeline = StreamingSTTPipeline(
        provider,
        result_callback=results.append,
    )

    pipeline.start()
    pipeline.push_audio(b"first")
    pipeline.finish()

    pipeline.start()
    pipeline.push_audio(b"second")
    pipeline.finish()

    assert len(results) == 4


def test_streaming_pipeline_start_is_idempotent():
    provider = FakeStreamingSTT()

    pipeline = StreamingSTTPipeline(
        provider,
        result_callback=lambda result: None,
    )

    pipeline.start()
    pipeline.start()

    assert pipeline.is_active is True
    assert provider.started is True


def test_streaming_pipeline_requires_callback():
    provider = FakeStreamingSTT()

    try:
        StreamingSTTPipeline(
            provider,
            result_callback=None,
        )
        assert False, "Expected TypeError"
    except TypeError:
        pass
