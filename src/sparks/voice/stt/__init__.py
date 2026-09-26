"""
SPARKS Speech-to-Text subsystem.
"""

from sparks.voice.stt.accumulator import TranscriptionAccumulator
from sparks.voice.stt.base import (
    SpeechToText,
    TranscriptionCallback,
)
from sparks.voice.stt.faster_whisper import FasterWhisperSTT
from sparks.voice.stt.types import (
    TranscriptionResult,
    TranscriptionType,
)

__all__ = [
    "FasterWhisperSTT",
    "SpeechToText",
    "TranscriptionAccumulator",
    "TranscriptionCallback",
    "TranscriptionResult",
    "TranscriptionType",
]
