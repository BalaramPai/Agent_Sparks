"""
SPARKS voice subsystem.

Provides domain contracts for microphone input,
voice activity detection, speech recognition,
voice state, and speech output.
"""

from sparks.voice.capture import (
    AudioCapture,
    AudioCaptureConfig,
    SoundDeviceCapture,
)
from sparks.voice.stt import (
    FasterWhisperSTT,
    SpeechToText,
    TranscriptionAccumulator,
    TranscriptionCallback,
    TranscriptionResult,
    TranscriptionType,
)
from sparks.voice.types import (
    VoiceEvent,
    VoiceEventType,
    VoiceState,
)
from sparks.voice.vad import (
    VadConfig,
    VadEngine,
    VadEvent,
    VadEventType,
    VoiceActivityDetector,
    VoiceActivityFrame,
)

__all__ = [
    "AudioCapture",
    "AudioCaptureConfig",
    "SoundDeviceCapture",
    "FasterWhisperSTT",
    "SpeechToText",
    "TranscriptionAccumulator",
    "TranscriptionCallback",
    "TranscriptionResult",
    "TranscriptionType",
    "VadConfig",
    "VadEngine",
    "VadEvent",
    "VadEventType",
    "VoiceActivityDetector",
    "VoiceActivityFrame",
    "VoiceEvent",
    "VoiceEventType",
    "VoiceState",
]
