from __future__ import annotations

import time
import sounddevice as sd

from sparks.voice.stt.faster_whisper import FasterWhisperSTT


SAMPLE_RATE = 16_000
CHANNELS = 1
RECORD_SECONDS = 6


def record_audio() -> bytes:
    print("\n[SPEARKS] Listening...")
    print("[VOICE ] Speak now.")

    audio = sd.rec(
        int(RECORD_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
    )

    sd.wait()

    return audio.tobytes()


def transcribe(stt: FasterWhisperSTT, audio: bytes) -> str:
    result = []

    def on_result(item) -> None:
        if item.text.strip():
            result.append(item.text.strip())

    started = time.perf_counter()

    stt.transcribe([audio], on_result)

    elapsed = time.perf_counter() - started

    text = " ".join(result).strip()

    print(f"[STT   ] {elapsed:.3f}s")
    print(f"[VOICE ] {text or '<no speech detected>'}")

    return text


def main() -> None:
    print("=" * 60)
    print("                 SPARKS VOICE CONSOLE")
    print("=" * 60)
    print()
    print("Local microphone + Faster-Whisper")
    print("Press Ctrl+C to exit.")
    print()

    stt = FasterWhisperSTT(
        model_size="base",
        device="cpu",
        compute_type="int8",
    )

    print("[MODEL ] Loading Faster-Whisper...")
    load_started = time.perf_counter()
    stt.load()
    print(f"[MODEL ] Ready in {time.perf_counter() - load_started:.3f}s")

    while True:
        input("\nPress ENTER to speak...")

        audio = record_audio()

        print("[STATE ] Transcribing...")
        text = transcribe(stt, audio)

        if text:
            print(f"[SPARKS] Heard: {text}")


if __name__ == "__main__":
    main()
