from sparks.tools.runtime import SparksCommandRuntime


def test_runtime_routes_open_chrome(monkeypatch) -> None:
    runtime = SparksCommandRuntime()

    expected = {
        "success": True,
        "tool_name": "open_chrome",
        "message": "Google Chrome opened successfully.",
    }

    monkeypatch.setattr(
        "sparks.tools.application.chrome.OpenChromeTool.execute",
        lambda self, arguments, context: type(
            "Result",
            (),
            expected,
        )(),
    )

    result = runtime.execute("Open Chrome")

    assert result is not None
    assert result.success is True
    assert result.tool_name == "open_chrome"


def test_runtime_ignores_non_deterministic_request() -> None:
    runtime = SparksCommandRuntime()

    result = runtime.execute(
        "Explain this error in my Python code"
    )

    assert result is None
