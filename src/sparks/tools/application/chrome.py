from __future__ import annotations

import os
import subprocess
from pathlib import Path

from sparks.tools.base import Tool
from sparks.tools.types import ToolContext, ToolResult


class OpenChromeTool(Tool):
    name = "open_chrome"
    description = "Open Google Chrome."

    _COMMANDS = (
        "open chrome",
        "open google chrome",
        "launch chrome",
        "launch google chrome",
        "start chrome",
        "start google chrome",
    )

    def can_handle(self, text: str) -> bool:
        normalized = " ".join(text.strip().lower().split())
        return normalized in self._COMMANDS

    def _find_chrome(self) -> str | None:
        candidates = []

        program_files = os.environ.get("PROGRAMFILES")
        if program_files:
            candidates.append(
                Path(program_files)
                / "Google"
                / "Chrome"
                / "Application"
                / "chrome.exe"
            )

        program_files_x86 = os.environ.get("PROGRAMFILES(X86)")
        if program_files_x86:
            candidates.append(
                Path(program_files_x86)
                / "Google"
                / "Chrome"
                / "Application"
                / "chrome.exe"
            )

        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            candidates.append(
                Path(local_app_data)
                / "Google"
                / "Chrome"
                / "Application"
                / "chrome.exe"
            )

        for candidate in candidates:
            if candidate.exists():
                return str(candidate)

        return None

    def _verify_running(self) -> bool:
        verification = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq chrome.exe"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

        return "chrome.exe" in verification.stdout.lower()

    def execute(
        self,
        arguments: dict,
        context: ToolContext,
    ) -> ToolResult:
        executable = self._find_chrome()

        if executable is None:
            return ToolResult(
                success=False,
                tool_name=self.name,
                message="Google Chrome executable was not found.",
                error="chrome_not_found",
            )

        try:
            subprocess.Popen(
                [executable],
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )

            verified = self._verify_running()

            if not verified:
                return ToolResult(
                    success=False,
                    tool_name=self.name,
                    message="Chrome launch was attempted but could not be verified.",
                    error="verification_failed",
                    data={
                        "executable": executable,
                        "verified": False,
                    },
                )

            return ToolResult(
                success=True,
                tool_name=self.name,
                message="Google Chrome opened successfully.",
                data={
                    "executable": executable,
                    "verified": True,
                },
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                tool_name=self.name,
                message="Failed to open Google Chrome.",
                error=str(exc),
                data={
                    "executable": executable,
                    "verified": False,
                },
            )
