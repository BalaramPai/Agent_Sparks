from __future__ import annotations

import sys

from sparks.tools.runtime import SparksCommandRuntime


def main() -> int:
    command = (
        " ".join(sys.argv[1:]).strip()
        if len(sys.argv) > 1
        else "Open Chrome"
    )

    print()
    print("=" * 70)
    print("SPARKS — REAL COMMAND EXECUTION")
    print("=" * 70)
    print()
    print(f"User command : {command}")

    runtime = SparksCommandRuntime()

    routed = runtime.router.route(command)

    print(f"Route        : {routed.route.value}")
    print(f"Confidence   : {routed.confidence}")
    print(f"Reason       : {routed.reason}")

    result = runtime.execute(command)

    if result is None:
        print()
        print("No deterministic tool execution.")
        print("The request should continue through the inference/agent path.")
        return 0

    print()
    print(f"Tool         : {result.tool_name}")
    print(f"Success      : {result.success}")
    print(f"Message      : {result.message}")

    if result.data:
        print(f"Data         : {result.data}")

    if result.error:
        print(f"Error        : {result.error}")

    print()
    print("=" * 70)

    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
