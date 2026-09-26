from pathlib import Path

files = [
    "src/sparks/voice/pipeline.py",
    "src/sparks/voice/cancellation.py",
    "src/sparks/voice/stt/base.py",
    "src/sparks/voice/stt/faster_whisper.py",
]

for file in files:
    print("\n" + "=" * 90)
    print(file)
    print("=" * 90)

    path = Path(file)

    if not path.exists():
        print("MISSING")
        continue

    print(path.read_text(encoding="utf-8"))
