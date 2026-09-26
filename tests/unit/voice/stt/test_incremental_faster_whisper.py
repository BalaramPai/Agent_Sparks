import threading
import time

import pytest

from sparks.voice.stt.incremental_faster_whisper import (
    IncrementalFasterWhisperSTT,
)
from sparks.voice.stt.streaming import StreamingTranscriptionType


class FakeSegment:
    def __init__(self, text):
        self.text = text


class FakeModel:
    def __init__(self):
        self.calls = 0

    def transcribe(self, audio, **kwargs):
        self.calls += 1
        return iter([FakeSegment("open chrome")]), None


def test_rejects_invalid_intervals():
    with pytest.raises(ValueError):
        IncrementalFasterWhisperSTT(partial_interval=0)

    with pytest.raises(ValueError):
        IncrementalFasterWhisperSTT(min_audio_duration=0)


def test_start_loads_model(monkeypatch):
    stt = IncrementalFasterWhisperSTT()

    fake_model = FakeModel()

    monkeypatch.setattr(stt, "_model", fake_model)

    stt.start()

    assert stt.is_active is True

    stt.cancel()


def test_push_audio_requires_active_stream():
    stt = IncrementalFasterWhisperSTT()

    with pytest.raises(RuntimeError):
        stt.push_audio(b"audio")


def test_incremental_transcription_emits_partial():
    stt = IncrementalFasterWhisperSTT(
        partial_interval=0.01,
        min_audio_duration=0.01,
    )

    stt._model = FakeModel()

    results = []

    stt.start()
    stt._callback = results.append

    stt.push_audio(b"\x01\x00" * 400)

    deadline = time.time() + 1.0

    while not results and time.time() < deadline:
        time.sleep(0.01)

    stt.cancel()

    assert results
    assert results[0].result_type == StreamingTranscriptionType.PARTIAL
    assert results[0].text == "open chrome"


def test_finish_emits_final():
    stt = IncrementalFasterWhisperSTT(
        partial_interval=10.0,
        min_audio_duration=10.0,
    )

    stt._model = FakeModel()

    results = []

    stt.start()
    stt.push_audio(b"\x01\x00" * 400)

    stt.finish(results.append)

    assert results
    assert results[-1].result_type == StreamingTranscriptionType.FINAL
    assert results[-1].text == "open chrome"

    assert stt.is_active is False


def test_cancel_stops_stream():
    stt = IncrementalFasterWhisperSTT()

    stt._model = FakeModel()
    stt.start()

    assert stt.is_active is True

    stt.cancel()

    assert stt.is_active is False


def test_cancel_wakes_worker_immediately():
    stt = IncrementalFasterWhisperSTT(
        partial_interval=30.0,
    )

    stt._model = FakeModel()
    stt.start()

    started = time.perf_counter()

    stt.cancel()

    elapsed = time.perf_counter() - started

    assert stt.is_active is False
    assert elapsed < 1.0


def test_finish_wakes_worker_immediately():
    stt = IncrementalFasterWhisperSTT(
        partial_interval=30.0,
        min_audio_duration=30.0,
    )

    stt._model = FakeModel()

    results = []

    stt.start()
    stt.push_audio(b"\x01\x00" * 400)

    started = time.perf_counter()

    stt.finish(results.append)

    elapsed = time.perf_counter() - started

    assert results[-1].result_type == StreamingTranscriptionType.FINAL
    assert stt.is_active is False
    assert elapsed < 1.0


def test_no_worker_thread_remains_after_finish():
    stt = IncrementalFasterWhisperSTT(
        partial_interval=30.0,
    )

    stt._model = FakeModel()

    stt.start()
    stt.push_audio(b"\x01\x00" * 400)

    stt.finish(lambda _: None)

    assert stt._worker is None

    alive = [
        thread
        for thread in threading.enumerate()
        if thread.name == "sparks-whisper-stream"
    ]

    assert alive == []
