from unittest.mock import Mock

from sparks.tools.types import ToolResult
from sparks.voice.command_executor import VoiceCommandExecutor


def test_voice_command_executor_forwards_transcript() -> None:
    runtime = Mock()
    expected = ToolResult(
        success=True,
        tool_name="open_chrome",
        message="Google Chrome opened successfully.",
    )
    runtime.execute.return_value = expected

    executor = VoiceCommandExecutor(runtime=runtime)

    result = executor.execute("open Chrome")

    runtime.execute.assert_called_once_with("open Chrome")
    assert result is expected


def test_voice_command_executor_ignores_empty_transcript() -> None:
    runtime = Mock()
    executor = VoiceCommandExecutor(runtime=runtime)

    result = executor.execute("   ")

    assert result is None
    runtime.execute.assert_not_called()
