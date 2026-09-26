from collections import deque
from threading import Event
from time import monotonic

from sparks.voice.capture.base import AudioCaptureConfig
from sparks.voice.pipeline import VoicePipeline
from sparks.voice.types import VoiceEventType, VoiceState
from sparks.voice.stt.types import TranscriptionResult, TranscriptionType


class FakeCapture:
    def __init__(self) -> None:
        self.config = AudioCaptureConfig()
        self.callback = None
        self.started = False
        self.stopped = False

    def start(self, callback) -> None:
        self.callback = callback
        self.started = True

    def stop(self) -> None:
        self.stopped = True

    def emit(self, audio: bytes) -> None:
        self.callback(audio)


class FakeDetector:
    def __init__(self, speech_pattern: list[bool]) -> None:
        self.speech_pattern = deque(speech_pattern)

    def is_speech(self, frame) -> bool:
        return self.speech_pattern.popleft()


class FakeSTT:
    def __init__(self) -> None:
        self.calls = []
        self.cancelled = False

    def transcribe(self, audio_chunks, callback) -> None:
        self.calls.append(tuple(audio_chunks))
        callback(
            TranscriptionResult(
                text="hello sparks",
                result_type=TranscriptionType.FINAL,
                confidence=0.9,
                language="en",
            )
        )

    def cancel(self) -> None:
        self.cancelled = True


class BlockingSTT(FakeSTT):
    def __init__(self) -> None:
        super().__init__()
        self.started = Event()
        self.release = Event()

    def transcribe(self, audio_chunks, callback) -> None:
        self.started.set()
        self.release.wait(timeout=2)
        super().transcribe(audio_chunks, callback)


class FakeVad:
    def __init__(self, speech_pattern: list[bool]) -> None:
        from sparks.voice.vad.engine import VadConfig, VadEngine

        self.engine = VadEngine(
            FakeDetector(speech_pattern),
            VadConfig(
                speech_start_frames=2,
                speech_stop_frames=2,
            ),
        )

    @property
    def is_speaking(self):
        return self.engine.is_speaking

    def process(self, frame):
        return self.engine.process(frame)

    def reset(self):
        self.engine.reset()


def wait_for_calls(stt, timeout: float = 2) -> None:
    deadline = monotonic() + timeout

    while not stt.calls and monotonic() < deadline:
        pass


def test_pipeline_transcribes_completed_utterance():
    capture = FakeCapture()
    vad = FakeVad([False, True, True, True, False, False])
    stt = FakeSTT()

    events = []

    pipeline = VoicePipeline(
        capture,
        vad,
        stt,
        event_callback=events.append,
    )

    pipeline.start()

    for index in range(6):
        capture.emit(bytes([index]) * 640)

    wait_for_calls(stt)

    assert stt.calls

    event_types = [
        event.event_type
        for event in events
    ]

    assert VoiceEventType.LISTENING_STARTED in event_types
    assert VoiceEventType.SPEECH_STARTED in event_types
    assert VoiceEventType.SPEECH_STOPPED in event_types
    assert VoiceEventType.TRANSCRIPTION_STARTED in event_types
    assert VoiceEventType.TRANSCRIPTION_COMPLETED in event_types

    completed = [
        event
        for event in events
        if event.event_type
        == VoiceEventType.TRANSCRIPTION_COMPLETED
    ][0]

    assert completed.text == "hello sparks"
    assert completed.confidence == 0.9

    pipeline.stop()


def test_pipeline_preserves_pre_roll():
    capture = FakeCapture()
    vad = FakeVad([True, True, False, False, False])
    stt = FakeSTT()

    pipeline = VoicePipeline(
        capture,
        vad,
        stt,
        pre_roll_frames=2,
    )

    pipeline.start()

    capture.emit(b"frame-1")
    capture.emit(b"frame-2")
    capture.emit(b"frame-3")
    capture.emit(b"frame-4")

    wait_for_calls(stt)

    assert stt.calls
    assert b"frame-1" in stt.calls[0]

    pipeline.stop()


def test_pipeline_does_not_transcribe_without_speech():
    capture = FakeCapture()
    vad = FakeVad([False, False, False, False])
    stt = FakeSTT()

    pipeline = VoicePipeline(
        capture,
        vad,
        stt,
    )

    pipeline.start()

    for _ in range(4):
        capture.emit(b"silence")

    assert stt.calls == []

    pipeline.stop()


def test_pipeline_stop_resets_state():
    capture = FakeCapture()
    vad = FakeVad([])
    stt = FakeSTT()

    pipeline = VoicePipeline(
        capture,
        vad,
        stt,
    )

    pipeline.start()
    pipeline.stop()

    assert pipeline.state == VoiceState.IDLE
    assert not pipeline.is_running
    assert capture.stopped
    assert stt.cancelled


def test_pipeline_does_not_block_capture_while_stt_runs():
    capture = FakeCapture()
    vad = FakeVad([True, True, False, False, False])
    stt = BlockingSTT()

    events = []

    pipeline = VoicePipeline(
        capture,
        vad,
        stt,
        event_callback=events.append,
    )

    pipeline.start()

    capture.emit(b"frame-1")
    capture.emit(b"frame-2")
    capture.emit(b"frame-3")
    capture.emit(b"frame-4")

    assert stt.started.wait(timeout=2)

    start = monotonic()

    capture.emit(b"frame-5")

    elapsed = monotonic() - start

    assert elapsed < 0.1

    assert pipeline.state == VoiceState.TRANSCRIBING

    stt.release.set()

    pipeline.stop()
def test_pipeline_does_not_block_capture_while_stt_runs():
    capture = FakeCapture()
    vad = FakeVad([True, True, False, False, False])
    stt = BlockingSTT()

    events = []

    pipeline = VoicePipeline(
        capture,
        vad,
        stt,
        event_callback=events.append,
    )

    pipeline.start()

    capture.emit(b"frame-1")
    capture.emit(b"frame-2")
    capture.emit(b"frame-3")
    capture.emit(b"frame-4")

    assert stt.started.wait(timeout=2)

    start = monotonic()

    capture.emit(b"frame-5")

    elapsed = monotonic() - start

    assert elapsed < 0.1

    assert pipeline.state == VoiceState.TRANSCRIBING

    stt.release.set()

    pipeline.stop()
def test_pipeline_stop_during_stt_returns_to_idle():
    capture = FakeCapture()
    vad = FakeVad([True, True, False, False, False])
    stt = BlockingSTT()

    pipeline = VoicePipeline(
        capture,
        vad,
        stt,
    )

    pipeline.start()

    capture.emit(b"frame-1")
    capture.emit(b"frame-2")
    capture.emit(b"frame-3")
    capture.emit(b"frame-4")

    assert stt.started.wait(timeout=2)

    pipeline.stop()

    assert not pipeline.is_running
    assert pipeline.state == VoiceState.IDLE
    assert capture.stopped
    assert stt.cancelled

    stt.release.set()
class FailingSTT(FakeSTT):
    def transcribe(self, audio_chunks, callback) -> None:
        raise RuntimeError("STT provider failed")


def test_pipeline_handles_stt_failure():
    capture = FakeCapture()
    vad = FakeVad([True, True, False, False, False])
    stt = FailingSTT()

    events = []

    pipeline = VoicePipeline(
        capture,
        vad,
        stt,
        event_callback=events.append,
    )

    pipeline.start()

    capture.emit(b"frame-1")
    capture.emit(b"frame-2")
    capture.emit(b"frame-3")
    capture.emit(b"frame-4")

    deadline = monotonic() + 2

    while (
        pipeline.state != VoiceState.ERROR
        and monotonic() < deadline
    ):
        pass

    assert pipeline.state == VoiceState.ERROR

    error_events = [
        event
        for event in events
        if event.event_type == VoiceEventType.ERROR
    ]

    assert error_events
    assert error_events[-1].metadata["error"] == "STT provider failed"
    assert error_events[-1].metadata["error_type"] == "RuntimeError"

    pipeline.stop()

    assert pipeline.state == VoiceState.IDLE
def test_pipeline_can_restart_after_stt_failure():
    capture = FakeCapture()
    vad = FakeVad([
        True, True, False, False, False,
    ])
    stt = FailingSTT()

    pipeline = VoicePipeline(
        capture,
        vad,
        stt,
    )

    pipeline.start()

    capture.emit(b"frame-1")
    capture.emit(b"frame-2")
    capture.emit(b"frame-3")
    capture.emit(b"frame-4")

    deadline = monotonic() + 2

    while (
        pipeline.state != VoiceState.ERROR
        and monotonic() < deadline
    ):
        pass

    assert pipeline.state == VoiceState.ERROR

    pipeline.stop()

    assert pipeline.state == VoiceState.IDLE

    pipeline.start()

    assert pipeline.is_running
    assert pipeline.state == VoiceState.LISTENING

    pipeline.stop()
def test_pipeline_start_is_idempotent():
    capture = FakeCapture()
    vad = FakeVad([])
    stt = FakeSTT()

    pipeline = VoicePipeline(
        capture,
        vad,
        stt,
    )

    pipeline.start()

    first_executor = pipeline._executor

    pipeline.start()

    assert pipeline.is_running
    assert pipeline.state == VoiceState.LISTENING
    assert pipeline._executor is first_executor

    pipeline.stop()
from sparks.voice.command_executor import VoiceCommandExecutor
from sparks.tools.types import ToolResult


class FakeCommandExecutor:
    def __init__(self, result=None) -> None:
        self.calls = []
        self.result = result or ToolResult(
            success=True,
            tool_name="open_chrome",
            message="Google Chrome opened successfully.",
            data={"verified": True},
        )

    def execute(self, transcript: str):
        self.calls.append(transcript)
        return self.result


def test_pipeline_executes_command_from_final_transcription():
    capture = FakeCapture()
    vad = FakeVad([True, True, False, False, False])
    stt = FakeSTT()
    command_executor = FakeCommandExecutor()

    events = []

    pipeline = VoicePipeline(
        capture,
        vad,
        stt,
        command_executor=command_executor,
        event_callback=events.append,
    )

    pipeline.start()

    capture.emit(b"frame-1")
    capture.emit(b"frame-2")
    capture.emit(b"frame-3")
    capture.emit(b"frame-4")

    deadline = monotonic() + 2

    while (
        not command_executor.calls
        and monotonic() < deadline
    ):
        pass

    assert command_executor.calls == ["hello sparks"]

    action_events = [
        event
        for event in events
        if event.event_type == VoiceEventType.ACTION_COMPLETED
    ]

    assert action_events
    assert action_events[-1].text == "Google Chrome opened successfully."
    assert action_events[-1].metadata["tool_name"] == "open_chrome"
    assert action_events[-1].metadata["success"] is True

    pipeline.stop()


def test_pipeline_does_not_execute_command_from_partial_transcription():
    capture = FakeCapture()
    vad = FakeVad([True, True, False, False, False])
    stt = FakeSTT()
    command_executor = FakeCommandExecutor()

    pipeline = VoicePipeline(
        capture,
        vad,
        stt,
        command_executor=command_executor,
    )

    pipeline.start()

    capture.emit(b"frame-1")
    capture.emit(b"frame-2")
    capture.emit(b"frame-3")
    capture.emit(b"frame-4")

    deadline = monotonic() + 2

    while (
        not command_executor.calls
        and monotonic() < deadline
    ):
        pass

    assert command_executor.calls == ["hello sparks"]

    pipeline.stop()


def test_pipeline_action_failure_emits_error_event():
    capture = FakeCapture()
    vad = FakeVad([True, True, False, False, False])
    stt = FakeSTT()

    class FailingCommandExecutor:
        def execute(self, transcript: str):
            raise RuntimeError("tool execution failed")

    events = []

    pipeline = VoicePipeline(
        capture,
        vad,
        stt,
        command_executor=FailingCommandExecutor(),
        event_callback=events.append,
    )

    pipeline.start()

    capture.emit(b"frame-1")
    capture.emit(b"frame-2")
    capture.emit(b"frame-3")
    capture.emit(b"frame-4")

    deadline = monotonic() + 2

    while (
        not any(
            event.event_type == VoiceEventType.ERROR
            for event in events
        )
        and monotonic() < deadline
    ):
        pass

    error_events = [
        event
        for event in events
        if event.event_type == VoiceEventType.ERROR
    ]

    assert error_events
    assert error_events[-1].metadata["error"] == "tool execution failed"
    assert error_events[-1].metadata["error_type"] == "RuntimeError"

    pipeline.stop()
