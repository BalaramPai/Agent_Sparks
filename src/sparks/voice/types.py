from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class VoiceState(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"
    DETECTING_SPEECH = "detecting_speech"
    TRANSCRIBING = "transcribing"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    INTERRUPTED = "interrupted"
    ERROR = "error"


class VoiceEventType(str, Enum):
    LISTENING_STARTED = "voice.listening_started"
    SPEECH_STARTED = "voice.speech_started"
    SPEECH_STOPPED = "voice.speech_stopped"

    TRANSCRIPTION_STARTED = "voice.transcription_started"
    TRANSCRIPTION_PARTIAL = "voice.transcription_partial"
    TRANSCRIPTION_COMPLETED = "voice.transcription_completed"

    PROCESSING_STARTED = "voice.processing_started"
    ACTION_COMPLETED = "voice.action_completed"

    SPEAKING_STARTED = "voice.speaking_started"
    SPEAKING_STOPPED = "voice.speaking_stopped"
    SPEAKING_INTERRUPTED = "voice.speaking_interrupted"

    ERROR = "voice.error"


@dataclass(frozen=True)
class VoiceEvent:
    event_type: VoiceEventType
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    text: str | None = None
    state: VoiceState | None = None
    confidence: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
