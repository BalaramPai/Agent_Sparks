from sparks.tools.application.url import OpenUrlTool


def test_url_tool_handles_https_url() -> None:
    tool = OpenUrlTool()

    assert tool.can_handle("open https://youtube.com")
    assert tool.can_handle("open www.google.com")


def test_url_tool_rejects_non_url_command() -> None:
    tool = OpenUrlTool()

    assert not tool.can_handle("open chrome")


def test_url_tool_opens_url(monkeypatch) -> None:
    tool = OpenUrlTool()

    opened: list[str] = []

    monkeypatch.setattr(
        "sparks.tools.application.url.webbrowser.open",
        lambda url: opened.append(url) or True,
    )

    result = tool.execute(
        {"text": "open https://youtube.com"},
        context=None,
    )

    assert result.success is True
    assert result.tool_name == "open_url"
    assert opened == ["https://youtube.com"]
