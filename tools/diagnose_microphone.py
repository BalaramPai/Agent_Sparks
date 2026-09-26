import time

import numpy as np
import sounddevice as sd


SAMPLE_RATE = 16_000
CHANNELS = 1
DURATION_SECONDS = 6


def main() -> None:
    print()
    print("=" * 60)
    print("SPARKS - MICROPHONE SIGNAL DIAGNOSTIC")
    print("=" * 60)
    print()

    input("Press ENTER when ready...")

    print()
    print("Recording starts in 1 second...")
    time.sleep(1)

    print("SPEAK NOW")

    audio = sd.rec(
        int(DURATION_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
    )

    sd.wait()

    samples = audio[:, 0].astype(np.float32)

    peak = float(np.max(np.abs(samples)))
    rms = float(np.sqrt(np.mean(samples ** 2)))

    print()
    print("=" * 60)
    print("SIGNAL RESULT")
    print("=" * 60)
    print(f"Peak amplitude : {peak:.2f}")
    print(f"RMS amplitude  : {rms:.2f}")
    print(f"Min sample     : {np.min(samples):.2f}")
    print(f"Max sample     : {np.max(samples):.2f}")
    print()

    if peak < 100:
        print("WARNING: Signal is extremely quiet.")
    elif peak < 1000:
        print("WARNING: Signal is very quiet.")
    else:
        print("Microphone signal detected.")

    print()
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
