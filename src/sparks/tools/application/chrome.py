from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from sparks.tools.base import Tool
from sparks.tools.types import ToolContext, ToolResult


class OpenChromeTool(Tool):
    name = "open_chrome"
    description = "Open Google Chrome and verify that the Chrome process is running."

    def execute(
        self,
        arguments: dict[str, Any],
        context: ToolContext,
    ) -> ToolResult:
        del arguments
        del context

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
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except OSError as exc:
            return ToolResult(
                success=False,
                tool_name=self.name,
                message="Failed to launch Google Chrome.",
                error=str(exc),
            )

        verified = self._verify_running()

        if not verified:
            return ToolResult(
                success=False,
                tool_name=self.name,
                message="Chrome launch was requested, but process verification failed.",
                data={"executable": executable},
                error="verification_failed",
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

    @staticmethod
    def _find_chrome() -> str | None:
        candidates: list[str] = []

        path = shutil.which("chrome.exe")
        if path:
            candidates.append(path)

        local_app_data = os.environ.get("LOCALAPPDATA")
        program_files = os.environ.get("PROGRAMFILES")
        program_files_x86 = os.environ.get("PROGRAMFILES(X86)")

        if local_app_data:
            candidates.append(
                str(
                    Path(local_app_data)
                    / "Google"
                    / "Chrome"
                    / "Application"
                    / "chrome.exe"
                )
            )

        if program_files:
            candidates.append(
                str(
                    Path(program_files)
                    / "Google"
                    / "Chrome"
                    / "Application"
                    / "chrome.exe"
                )
            )

        if program_files_x86:
            candidates.append(
                str(
                    Path(program_files_x86)
                    / "Google"
                    / "Chrome"
                    / "Application"
                    / "chrome.exe"
                )
            )

        for candidate in candidates:
            if Path(candidate).is_file():
                return candidate

        return None

    @staticmethod
    def _verify_running(timeout: float = 5.0) -> bool:
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            try:
                result = subprocess.run(
                    [
                        "tasklist",
                        "/FI",
                        "IMAGENAME eq chrome.exe",
                        "/FO",
                        "CSV",
                        "/NH",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=2,
                    creationflags=getattr(
                        subprocess,
                        "CREATE_NO_WINDOW",
                        0,
                    ),
                )

                if "chrome.exe" in result.stdout.lower():
                    return True

            except (OSError, subprocess.SubprocessError):
                pass

            time.sleep(0.25)

        return False
