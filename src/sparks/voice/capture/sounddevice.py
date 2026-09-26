from collections.abc import Callable
from typing import Any

import sounddevice as sd

from sparks.voice.capture.base import (
    AudioCapture,
    AudioCaptureConfig,
)


AudioCallback = Callable[[bytes], None]


class SoundDeviceCapture(AudioCapture):
    """
    Microphone capture implementation backed by PortAudio
    through python-sounddevice.

    Raw microphone data remains in-memory and is forwarded
    to the supplied callback. This class does not persist audio.
    """

    def __init__(
        self,
        config: AudioCaptureConfig | None = None,
        device: int | str | None = None,
    ) -> None:
        super().__init__(config)
        self.device = device
        self._stream: sd.RawInputStream | None = None
        self._callback: AudioCallback | None = None

    def start(self, callback: AudioCallback) -> None:
        if self.is_running:
            return

        if not callable(callback):
            raise TypeError("callback must be callable")

        self._callback = callback

        try:
            self._stream = sd.RawInputStream(
                samplerate=self.config.sample_rate,
                blocksize=self.config.block_size,
                device=self.device,
                channels=self.config.channels,
                dtype="int16",
                callback=self._handle_audio,
            )

            self._stream.start()
            self._running = True

        except Exception:
            self._stream = None
            self._callback = None
            self._running = False
            raise

    def stop(self) -> None:
        if self._stream is None:
            self._running = False
            self._callback = None
            return

        try:
            self._stream.stop()
            self._stream.close()
        finally:
            self._stream = None
            self._callback = None
            self._running = False

    def _handle_audio(
        self,
        indata: Any,
        frames: int,
        time: Any,
        status: Any,
    ) -> None:
        del frames, time

        if status:
            # Audio overflow/underflow information is intentionally
            # handled later by the voice telemetry layer.
            pass

        callback = self._callback

        if callback is None or not self._running:
            return

        callback(bytes(indata))
