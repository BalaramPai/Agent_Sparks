from __future__ import annotations

import re
import webbrowser

from sparks.tools.base import Tool
from sparks.tools.types import ToolContext, ToolResult


class OpenUrlTool(Tool):
    name = "open_url"
    description = "Open a URL in the user's default browser."

    _URL_PATTERN = re.compile(
        r"^(?:open|launch|go to)\s+"
        r"(https?://[^\s]+|www\.[^\s]+)$",
        re.IGNORECASE,
    )

    def can_handle(self, text: str) -> bool:
        return self._URL_PATTERN.match(text.strip()) is not None

    def _extract_url(self, text: str) -> str:
        match = self._URL_PATTERN.match(text.strip())

        if match is None:
            raise ValueError("Unable to extract URL from command.")

        url = match.group(1)

        if url.lower().startswith("www."):
            url = f"https://{url}"

        return url

    def execute(
        self,
        arguments: dict,
        context: ToolContext,
    ) -> ToolResult:
        text = str(arguments.get("text", "")).strip()

        if not text:
            return ToolResult(
                success=False,
                tool_name=self.name,
                message="No URL command was provided.",
                error="missing_command",
            )

        try:
            url = self._extract_url(text)

            opened = webbrowser.open(url)

            if not opened:
                return ToolResult(
                    success=False,
                    tool_name=self.name,
                    message=f"Failed to open {url}.",
                    error="browser_open_failed",
                    data={"url": url},
                )

            return ToolResult(
                success=True,
                tool_name=self.name,
                message=f"Opened {url}.",
                data={
                    "url": url,
                    "verified": True,
                },
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                tool_name=self.name,
                message="Failed to open URL.",
                error=str(exc),
            )
