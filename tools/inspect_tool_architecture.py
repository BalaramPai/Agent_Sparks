import inspect

print("\n" + "=" * 70)
print("SPARKS TOOL / ROUTER ARCHITECTURE INSPECTION")
print("=" * 70)

# Router
try:
    from sparks.router.router import IntentRouter

    print("\n[IntentRouter]")
    print("Class:", IntentRouter)
    print("Constructor:", inspect.signature(IntentRouter))
    print("Route:", inspect.signature(IntentRouter.route))

    router = IntentRouter()
    print("Instance:", router)

except Exception as exc:
    print("[IntentRouter ERROR]", type(exc).__name__, exc)


# Search likely tool modules
print("\n[TOOL MODULES]")

import sparks
import pathlib

root = pathlib.Path(sparks.__file__).parent

for path in root.rglob("*.py"):
    text = path.read_text(encoding="utf-8", errors="ignore")

    if any(
        term in text
        for term in [
            "class Tool",
            "ToolRegistry",
            "ToolExecution",
            "register_tool",
            "register(",
        ]
    ):
        print("\n---", path.relative_to(root), "---")

        for i, line in enumerate(text.splitlines(), 1):
            if any(
                term in line
                for term in [
                    "class Tool",
                    "ToolRegistry",
                    "ToolExecution",
                    "register_tool",
                    "def register",
                    "def execute",
                ]
            ):
                print(f"{i}: {line.strip()}")


print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
