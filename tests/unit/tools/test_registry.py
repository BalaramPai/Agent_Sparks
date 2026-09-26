from sparks.tools.application.chrome import OpenChromeTool
from sparks.tools.registry import ToolRegistry
from sparks.tools.types import ToolContext


def test_registry_registers_tool() -> None:
    registry = ToolRegistry()
    tool = OpenChromeTool()

    registry.register(tool)

    assert registry.list_tools() == ["open_chrome"]
    assert registry.get("open_chrome") is tool


def test_registry_rejects_duplicate_tool() -> None:
    registry = ToolRegistry()

    registry.register(OpenChromeTool())

    try:
        registry.register(OpenChromeTool())
        assert False, "Expected duplicate registration to fail"
    except ValueError as exc:
        assert "already registered" in str(exc)


def test_registry_unknown_tool() -> None:
    registry = ToolRegistry()

    try:
        registry.get("does_not_exist")
        assert False, "Expected unknown tool to fail"
    except KeyError as exc:
        assert "Unknown tool" in str(exc)


def test_chrome_tool_reports_missing_executable(monkeypatch) -> None:
    tool = OpenChromeTool()

    monkeypatch.setattr(
        tool,
        "_find_chrome",
        lambda: None,
    )

    result = tool.execute({}, ToolContext())

    assert result.success is False
    assert result.error == "chrome_not_found"


def test_chrome_tool_launch_and_verify(monkeypatch) -> None:
    tool = OpenChromeTool()

    monkeypatch.setattr(
        tool,
        "_find_chrome",
        lambda: r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    )

    launched: list[list[str]] = []

    class FakePopen:
        def __init__(self, args, **kwargs):
            launched.append(args)

    monkeypatch.setattr(
        "sparks.tools.application.chrome.subprocess.Popen",
        FakePopen,
    )

    monkeypatch.setattr(
        tool,
        "_verify_running",
        lambda: True,
    )

    result = tool.execute({}, ToolContext())

    assert result.success is True
    assert result.data["verified"] is True
    assert launched


def test_chrome_tool_reports_verification_failure(monkeypatch) -> None:
    tool = OpenChromeTool()

    monkeypatch.setattr(
        tool,
        "_find_chrome",
        lambda: r"C:\Chrome\chrome.exe",
    )

    monkeypatch.setattr(
        "sparks.tools.application.chrome.subprocess.Popen",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        tool,
        "_verify_running",
        lambda: False,
    )

    result = tool.execute({}, ToolContext())

    assert result.success is False
    assert result.error == "verification_failed"
