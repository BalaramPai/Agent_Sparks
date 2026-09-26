"""
SPARKS Voice Activity Detection subsystem.
"""

from sparks.voice.vad.base import (
    VoiceActivityDetector,
    VoiceActivityFrame,
)
from sparks.voice.vad.engine import (
    VadConfig,
    VadEngine,
    VadEvent,
    VadEventType,
)

__all__ = [
    "VoiceActivityDetector",
    "VoiceActivityFrame",
    "VadConfig",
    "VadEngine",
    "VadEvent",
    "VadEventType",
]
