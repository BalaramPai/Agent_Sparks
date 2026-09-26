from __future__ import annotations

import sys
import time

from sparks.router.router import IntentRouter
from sparks.voice.capture.base import AudioCaptureConfig
from sparks.voice.capture.sounddevice import SoundDeviceCapture
from sparks.voice.stt.faster_whisper import FasterWhisperSTT


def main() -> None:
    print("=" * 60)
    print("              SPARKS VOICE + ROUTER")
    print("=" * 60)
    print()
    print("MIC → STT → INTENT ROUTER")
    print("Press Ctrl+C to exit.")
    print()

    print("[MODEL ] Loading Faster-Whisper...")
    load_start = time.perf_counter()

    stt = FasterWhisperSTT(
        model_size="base",
        device="cpu",
        compute_type="int8",
        language="en",
    )
    stt.load()

    print(f"[MODEL ] Ready in {time.perf_counter() - load_start:.3f}s")
    print()

    router = IntentRouter()

    while True:
        print("-" * 60)
        print("Speak now...")
        print()

        audio_chunks: list[bytes] = []

        capture = SoundDeviceCapture(
            AudioCaptureConfig(
                sample_rate=16000,
                channels=1,
                block_size=320,
            )
        )

        capture.start(lambda chunk: audio_chunks.append(chunk))

        input("Press ENTER when finished speaking...")

        capture.stop()

        if not audio_chunks:
            print("[WARN  ] No audio captured.")
            continue

        print("[STT   ] Transcribing...")

        start = time.perf_counter()
        results = []

        stt.transcribe(
            audio_chunks,
            callback=lambda result: results.append(result),
        )

        elapsed = time.perf_counter() - start

        text = " ".join(
            result.text.strip()
            for result in results
            if result.text.strip()
        ).strip()

        print(f"[STT   ] {text}")
        print(f"[LAT   ] {elapsed:.3f}s")

        if not text:
            print("[ROUTER] No transcription.")
            continue

        print()
        print("[ROUTER] Processing...")

        try:
            result = router.route(text)

            print("[ROUTER] SUCCESS")
            print(f"[TEXT  ] {text}")
            print(f"[TYPE  ] {type(result).__name__}")
            print(f"[DATA  ] {result!r}")

            if hasattr(result, "__dict__"):
                print("[FIELDS]")
                for key, value in vars(result).items():
                    print(f"  {key}: {value}")

        except Exception as exc:
            print(
                f"[ERROR ] Router failed: "
                f"{type(exc).__name__}: {exc}"
            )

        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSPARKS stopped.")
        sys.exit(0)
