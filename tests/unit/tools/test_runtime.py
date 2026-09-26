from sparks.tools.runtime import SparksCommandRuntime


def test_runtime_selects_chrome_tool(monkeypatch) -> None:
    runtime = SparksCommandRuntime()

    executed: list[str] = []

    chrome = runtime.registry.get("open_chrome")

    monkeypatch.setattr(
        chrome,
        "execute",
        lambda arguments, context: executed.append(
            arguments["text"]
        ) or type(
            "Result",
            (),
            {
                "success": True,
                "tool_name": "open_chrome",
            },
        )(),
    )

    result = runtime.execute("open chrome")

    assert result is not None
    assert result.success is True
    assert result.tool_name == "open_chrome"
    assert executed == ["open chrome"]


def test_runtime_selects_url_tool(monkeypatch) -> None:
    runtime = SparksCommandRuntime()

    executed: list[str] = []

    url = runtime.registry.get("open_url")

    monkeypatch.setattr(
        url,
        "execute",
        lambda arguments, context: executed.append(
            arguments["text"]
        ) or type(
            "Result",
            (),
            {
                "success": True,
                "tool_name": "open_url",
            },
        )(),
    )

    result = runtime.execute("open https://youtube.com")

    assert result is not None
    assert result.success is True
    assert result.tool_name == "open_url"
    assert executed == ["open https://youtube.com"]


def test_runtime_returns_none_for_unknown_request() -> None:
    runtime = SparksCommandRuntime()

    result = runtime.execute(
        "send a message to my friend"
    )

    assert result is None


def test_runtime_returns_none_for_empty_request() -> None:
    runtime = SparksCommandRuntime()

    assert runtime.execute("") is None
    assert runtime.execute("   ") is None
