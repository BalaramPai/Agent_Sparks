from datetime import timezone

from sparks.voice.types import (
    VoiceEvent,
    VoiceEventType,
    VoiceState,
)


def test_voice_states_are_defined() -> None:
    assert VoiceState.IDLE.value == "idle"
    assert VoiceState.LISTENING.value == "listening"
    assert VoiceState.DETECTING_SPEECH.value == "detecting_speech"
    assert VoiceState.TRANSCRIBING.value == "transcribing"
    assert VoiceState.PROCESSING.value == "processing"
    assert VoiceState.SPEAKING.value == "speaking"
    assert VoiceState.INTERRUPTED.value == "interrupted"
    assert VoiceState.ERROR.value == "error"


def test_voice_event_types_are_defined() -> None:
    assert (
        VoiceEventType.LISTENING_STARTED.value
        == "voice.listening_started"
    )

    assert (
        VoiceEventType.TRANSCRIPTION_COMPLETED.value
        == "voice.transcription_completed"
    )

    assert (
        VoiceEventType.SPEAKING_INTERRUPTED.value
        == "voice.speaking_interrupted"
    )


def test_voice_event_defaults() -> None:
    event = VoiceEvent(
        event_type=VoiceEventType.LISTENING_STARTED,
    )

    assert event.event_type == VoiceEventType.LISTENING_STARTED
    assert event.state is None
    assert event.text is None
    assert event.confidence is None
    assert event.metadata == {}
    assert event.timestamp.tzinfo == timezone.utc


def test_voice_event_supports_transcription_data() -> None:
    event = VoiceEvent(
        event_type=VoiceEventType.TRANSCRIPTION_COMPLETED,
        state=VoiceState.TRANSCRIBING,
        text="What is the weather today?",
        confidence=0.97,
        metadata={
            "provider": "test",
        },
    )

    assert event.text == "What is the weather today?"
    assert event.state == VoiceState.TRANSCRIBING
    assert event.confidence == 0.97
    assert event.metadata["provider"] == "test"


def test_voice_event_is_immutable() -> None:
    event = VoiceEvent(
        event_type=VoiceEventType.LISTENING_STARTED,
    )

    try:
        event.text = "modified"
    except AttributeError:
        pass
    else:
        raise AssertionError("VoiceEvent must be immutable")
