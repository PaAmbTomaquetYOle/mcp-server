from __future__ import annotations

import subprocess

import pytest

from mcp_server import dev


class TestMcpInspectorLauncher:
    def test_build_inspector_command(self):
        assert dev.build_inspector_command() == [
            "npx",
            "--yes",
            "@modelcontextprotocol/inspector",
        ]

    def test_main_executes_npx_inspector(self, monkeypatch):
        captured = {}

        def fake_run(command, check):
            captured["command"] = command
            captured["check"] = check
            return subprocess.CompletedProcess(command, 0)

        monkeypatch.setattr(dev.subprocess, "run", fake_run)
        monkeypatch.setattr(dev.sys, "argv", ["mcp-inspector", "--port", "5173"])

        dev.main()

        assert captured["command"] == [
            "npx",
            "--yes",
            "@modelcontextprotocol/inspector",
            "--port",
            "5173",
        ]
        assert captured["check"] is True

    def test_main_errors_without_npx(self, monkeypatch):
        def fake_run(command, check):
            raise FileNotFoundError("npx")

        monkeypatch.setattr(dev.subprocess, "run", fake_run)

        with pytest.raises(RuntimeError, match="npx is required"):
            dev.main()
