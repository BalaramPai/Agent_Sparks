from pathlib import Path

files = [
    "src/sparks/voice/types.py",
    "src/sparks/voice/pipeline.py",
    "src/sparks/voice/stt/streaming.py",
    "src/sparks/voice/stt/streaming_pipeline.py",
]

for file in files:
    print()
    print("=" * 90)
    print(file)
    print("=" * 90)

    path = Path(file)

    if path.exists():
        print(path.read_text(encoding="utf-8"))
    else:
        print("MISSING")
