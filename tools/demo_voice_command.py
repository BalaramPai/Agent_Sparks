from __future__ import annotations

import math
import time
from array import array

from sparks.voice.capture.base import AudioCaptureConfig
from sparks.voice.capture.sounddevice import SoundDeviceCapture
from sparks.voice.command_executor import VoiceCommandExecutor
from sparks.voice.pipeline import VoicePipeline
from sparks.voice.stt.incremental_faster_whisper import (
    IncrementalFasterWhisperSTT,
)
from sparks.voice.types import VoiceEventType
from sparks.voice.vad.engine import VadConfig, VadEngine


class EnergyVAD:
    """Demo-only microphone energy detector."""

    def __init__(self, threshold: float = 700.0) -> None:
        self.threshold = threshold

    def is_speech(self, frame) -> bool:
        if not frame.audio:
            return False

        samples = array("h")
        samples.frombytes(frame.audio)

        if not samples:
            return False

        rms = math.sqrt(
            sum(sample * sample for sample in samples)
            / len(samples)
        )

        return rms >= self.threshold


def main() -> None:
    print("=" * 70)
    print("SPARKS - REAL VOICE COMMAND DEMO")
    print("=" * 70)
    print()
    print('Say: "Open Chrome"')
    print("Speak naturally, then pause.")
    print("Press Ctrl+C to stop.")
    print()

    config = AudioCaptureConfig(
        sample_rate=16_000,
        channels=1,
        block_size=320,
    )

    capture = SoundDeviceCapture(config=config)

    vad = VadEngine(
        EnergyVAD(threshold=700.0),
        VadConfig(
            speech_start_frames=2,
            speech_stop_frames=8,
        ),
    )

    stt = IncrementalFasterWhisperSTT(
        model_size="base",
        device="cpu",
        compute_type="int8",
        language="en",
        partial_interval=1.0,
        min_audio_duration=1.0,
    )

    command_executor = VoiceCommandExecutor()

    def on_event(event) -> None:
        if event.event_type == VoiceEventType.LISTENING_STARTED:
            print("[LISTENING]")

        elif event.event_type == VoiceEventType.SPEECH_STARTED:
            print("[SPEECH STARTED]")

        elif event.event_type == VoiceEventType.TRANSCRIPTION_PARTIAL:
            print(f"[PARTIAL] {event.text}")

        elif event.event_type == VoiceEventType.TRANSCRIPTION_COMPLETED:
            print(f"[FINAL] {event.text}")

        elif event.event_type == VoiceEventType.ACTION_COMPLETED:
            print()
            print("[ACTION COMPLETED]")
            print(f"Tool    : {event.metadata.get('tool_name')}")
            print(f"Success : {event.metadata.get('success')}")
            print(f"Message : {event.text}")
            print(f"Data    : {event.metadata.get('tool_data')}")
            print()

        elif event.event_type == VoiceEventType.ERROR:
            print()
            print("[ERROR]")
            print(event.metadata)
            print()

    pipeline = VoicePipeline(
        capture,
        vad,
        stt,
        streaming_stt=stt,
        command_executor=command_executor,
        event_callback=on_event,
    )

    try:
        print("Loading STT model...")
        stt.load()

        print("Starting voice pipeline...")
        pipeline.start()

        print()
        print("SPARKS IS LISTENING")
        print('Say: "Open Chrome"')
        print()

        while pipeline.is_running:
            time.sleep(0.1)

    except KeyboardInterrupt:
        print()
        print("Stopping SPARKS...")

    finally:
        pipeline.stop()

    print()
    print("=" * 70)
    print("VOICE COMMAND DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
