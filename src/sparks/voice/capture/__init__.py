"""
SPARKS microphone capture subsystem.
"""

from sparks.voice.capture.base import (
    AudioCapture,
    AudioCaptureConfig,
)
from sparks.voice.capture.sounddevice import SoundDeviceCapture

__all__ = [
    "AudioCapture",
    "AudioCaptureConfig",
    "SoundDeviceCapture",
]
