from sparks.tools.application.chrome import OpenChromeTool
from sparks.tools.application.url import OpenUrlTool
from sparks.tools.registry import ToolRegistry
from sparks.tools.selector import ToolSelector


def make_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(OpenChromeTool())
    registry.register(OpenUrlTool())
    return registry


def test_selector_finds_chrome() -> None:
    selector = ToolSelector(make_registry())

    result = selector.select("open chrome")

    assert result.tool is not None
    assert result.tool.name == "open_chrome"
    assert result.confidence == 1.0


def test_selector_finds_url() -> None:
    selector = ToolSelector(make_registry())

    result = selector.select("open https://youtube.com")

    assert result.tool is not None
    assert result.tool.name == "open_url"


def test_selector_returns_none_for_unknown_request() -> None:
    selector = ToolSelector(make_registry())

    result = selector.select("send a message to my friend")

    assert result.tool is None
    assert result.reason == "no_matching_tool"


def test_registry_exposes_descriptors() -> None:
    registry = make_registry()

    descriptors = registry.descriptors()

    assert {item.name for item in descriptors} == {
        "open_chrome",
        "open_url",
    }
