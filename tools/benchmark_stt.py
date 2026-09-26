import time

import sounddevice as sd

from sparks.voice.stt.faster_whisper import FasterWhisperSTT


SAMPLE_RATE = 16_000
CHANNELS = 1
DURATION_SECONDS = 6


def main() -> None:
    print()
    print("=" * 60)
    print("SPARKS - REAL STT BENCHMARK")
    print("=" * 60)
    print()
    print("Configuration")
    print("-" * 60)
    print(f"Sample rate : {SAMPLE_RATE} Hz")
    print(f"Channels    : {CHANNELS}")
    print(f"Duration    : {DURATION_SECONDS}s")
    print("Model       : tiny")
    print("Device      : CPU")
    print("Compute     : INT8")
    print()

    input("Press ENTER when ready...")

    print()
    print("Recording starts in 1 second...")
    time.sleep(1)

    print("SPEAK NOW")

    recording_start = time.perf_counter()

    audio = sd.rec(
        int(DURATION_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
    )

    sd.wait()

    recording_end = time.perf_counter()

    print("Recording finished.")
    print()

    pcm_bytes = audio.tobytes()

    print(f"Captured bytes : {len(pcm_bytes):,}")
    print(
        f"Recording time : "
        f"{recording_end - recording_start:.3f}s"
    )
    print()

    print("Loading Whisper tiny model...")

    load_start = time.perf_counter()

    stt = FasterWhisperSTT(
        model_size="tiny",
        device="cpu",
        compute_type="int8",
        language="en",
        beam_size=1,
        sample_rate=SAMPLE_RATE,
    )

    stt.load()

    load_end = time.perf_counter()

    print(
        f"Model load time: "
        f"{load_end - load_start:.3f}s"
    )
    print()

    results = []

    print("Transcribing...")

    transcription_start = time.perf_counter()

    stt.transcribe(
        [pcm_bytes],
        results.append,
    )

    transcription_end = time.perf_counter()

    processing_time = (
        transcription_end - transcription_start
    )

    print()
    print("=" * 60)
    print("RESULT")
    print("=" * 60)

    if results:
        transcript = " ".join(
            result.text
            for result in results
        )

        print(f"Transcript : {transcript}")
        print(f"Language   : {results[0].language}")
        print(f"Confidence : {results[0].confidence}")
    else:
        print("Transcript : <empty>")

    print()
    print(f"Transcription time : {processing_time:.3f}s")
    print(
        f"Realtime factor   : "
        f"{processing_time / DURATION_SECONDS:.3f}x"
    )

    print()
    print("=" * 60)
    print("BENCHMARK COMPLETE")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
