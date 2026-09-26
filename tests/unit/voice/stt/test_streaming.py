from __future__ import annotations

import pytest

from sparks.voice.stt.buffered_streaming import BufferedStreamingSTT
from sparks.voice.stt.streaming import (
    StreamingTranscriptionType,
)


class FakeProvider:
    def __init__(self):
        self.audio = None
        self.cancel_called = False

    def transcribe(self, audio_chunks, callback):
        self.audio = tuple(audio_chunks)

        callback(
            type(
                "Result",
                (),
                {
                    "text": "hello sparks",
                    "confidence": 0.91,
                    "language": "en",
                },
            )()
        )

    def cancel(self):
        self.cancel_called = True


def test_stream_starts_inactive():
    provider = FakeProvider()
    stream = BufferedStreamingSTT(provider)

    assert stream.is_active is False


def test_stream_accepts_incremental_audio():
    provider = FakeProvider()
    stream = BufferedStreamingSTT(provider)

    stream.start()

    stream.push_audio(b"one")
    stream.push_audio(b"two")
    stream.push_audio(b"three")

    assert stream.is_active is True


def test_stream_rejects_audio_before_start():
    provider = FakeProvider()
    stream = BufferedStreamingSTT(provider)

    with pytest.raises(RuntimeError):
        stream.push_audio(b"audio")


def test_finish_emits_final_result():
    provider = FakeProvider()
    stream = BufferedStreamingSTT(provider)

    results = []

    stream.start()
    stream.push_audio(b"one")
    stream.push_audio(b"two")

    stream.finish(results.append)

    assert len(results) == 1
    assert results[0].text == "hello sparks"
    assert results[0].result_type == StreamingTranscriptionType.FINAL
    assert results[0].confidence == 0.91
    assert results[0].language == "en"
    assert results[0].sequence == 1


def test_finish_passes_all_audio_to_provider():
    provider = FakeProvider()
    stream = BufferedStreamingSTT(provider)

    stream.start()

    stream.push_audio(b"hello")
    stream.push_audio(b" ")
    stream.push_audio(b"sparks")

    stream.finish(lambda result: None)

    assert provider.audio == (
        b"hello",
        b" ",
        b"sparks",
    )


def test_cancel_prevents_result():
    provider = FakeProvider()
    stream = BufferedStreamingSTT(provider)

    results = []

    stream.start()
    stream.push_audio(b"audio")
    stream.cancel()
    stream.finish(results.append)

    assert results == []
    assert provider.cancel_called is True


def test_cancel_before_start_is_safe():
    provider = FakeProvider()
    stream = BufferedStreamingSTT(provider)

    stream.cancel()

    assert provider.cancel_called is True


def test_stream_can_restart_after_finish():
    provider = FakeProvider()
    stream = BufferedStreamingSTT(provider)

    results = []

    stream.start()
    stream.push_audio(b"first")
    stream.finish(results.append)

    stream.start()
    stream.push_audio(b"second")
    stream.finish(results.append)

    assert len(results) == 2
    assert results[0].sequence == 1
    assert results[1].sequence == 1


def test_stream_can_restart_after_cancel():
    provider = FakeProvider()
    stream = BufferedStreamingSTT(provider)

    stream.start()
    stream.push_audio(b"cancelled")
    stream.cancel()

    stream.start()
    stream.push_audio(b"new")

    results = []
    stream.finish(results.append)

    assert len(results) == 1
    assert results[0].text == "hello sparks"
