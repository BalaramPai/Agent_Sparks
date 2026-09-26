from __future__ import annotations

import time

from sparks.voice.capture.sounddevice import SoundDeviceCapture
from sparks.voice.capture.base import AudioCaptureConfig
from sparks.voice.stt.incremental_faster_whisper import (
    IncrementalFasterWhisperSTT,
)
from sparks.voice.stt.streaming import StreamingTranscriptionType


def main() -> None:
    print("=" * 70)
    print("SPARKS — INCREMENTAL STREAMING STT")
    print("=" * 70)
    print()
    print("Speak naturally for a few seconds.")
    print("Press Ctrl+C to stop.")
    print()

    stt = IncrementalFasterWhisperSTT(
        model_size="base",
        device="cpu",
        compute_type="int8",
        language="en",
        partial_interval=1.0,
        min_audio_duration=1.0,
    )

    def on_result(result):
        kind = result.result_type.value.upper()
        print(f"[{kind}] {result.text}")

    stt.load()

    config = AudioCaptureConfig(
        sample_rate=16_000,
        channels=1,
        block_size=320,
    )

    capture = SoundDeviceCapture(config=config)

    stt.start(on_result)

    try:
        capture.start(stt.push_audio)

        while stt.is_active:
            time.sleep(0.1)

    except KeyboardInterrupt:
        print()
        print("Finishing transcription...")

    finally:
        try:
            capture.stop()
        except Exception:
            pass

        if stt.is_active:
            stt.finish()

    print()
    print("=" * 70)
    print("STREAMING STT DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
