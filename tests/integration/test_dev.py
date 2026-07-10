from __future__ import annotations

import subprocess

import pytest

from mcp_server import dev


class TestMcpInspectorLauncher:
    def test_build_npx_command(self):
        assert dev.build_npx_command() == [
            "npx.cmd" if dev.os.name == "nt" else "npx",
            "--yes",
            "@modelcontextprotocol/inspector@0.22.0",
        ]

    def test_build_server_command(self):
        assert dev.build_server_command() == [
            dev.sys.executable,
            "-m",
            "mcp_server.main",
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
            "npx.cmd" if dev.os.name == "nt" else "npx",
            "--yes",
            "@modelcontextprotocol/inspector@0.22.0",
            "--port",
            "5173",
        ]
        assert captured["check"] is True

    def test_ensure_local_server_running_starts_server_when_port_is_closed(self, monkeypatch):
        captured = {}

        class FakeServerProcess:
            def __init__(self):
                self.terminated = False

            def terminate(self):
                self.terminated = True

        def fake_is_port_open(host, port):
            return False

        def fake_wait_for_port(host, port, timeout_seconds):
            captured["waited_for"] = (host, port, timeout_seconds)

        def fake_popen(command):
            captured["command"] = command
            return FakeServerProcess()

        monkeypatch.setattr(dev, "is_port_open", fake_is_port_open)
        monkeypatch.setattr(dev, "wait_for_port", fake_wait_for_port)
        monkeypatch.setattr(dev.subprocess, "Popen", fake_popen)

        process = dev.ensure_local_server_running()

        assert captured["command"] == [
            dev.sys.executable,
            "-m",
            "mcp_server.main",
        ]
        assert captured["waited_for"] == (
            dev.LOCAL_SERVER_HOST,
            dev.LOCAL_SERVER_PORT,
            dev.SERVER_STARTUP_TIMEOUT_SECONDS,
        )
        assert process is not None

    def test_main_errors_without_npx_or_docker(self, monkeypatch):
        calls = []

        def fake_run(command, check):
            calls.append(command)
            raise FileNotFoundError("npx")

        monkeypatch.setattr(dev.subprocess, "run", fake_run)

        with pytest.raises(RuntimeError, match="Neither npx nor docker"):
            dev.main()

        assert calls[0][0] == ("npx.cmd" if dev.os.name == "nt" else "npx")
        assert calls[1][0] == "docker"

    def test_open_local_inspector_opens_browser_to_local_server(self, monkeypatch):
        captured = {}

        class FakeProcess:
            def __init__(self):
                self.terminated = False
                self.polled = False

            def wait(self):
                captured["waited"] = True

            def poll(self):
                self.polled = True
                return None

            def terminate(self):
                self.terminated = True

        def fake_popen(command):
            captured["command"] = command
            return FakeProcess()

        server_process = FakeProcess()

        def fake_ensure_local_server_running():
            captured["server_started"] = True
            return server_process

        def fake_sleep(seconds):
            captured["slept"] = seconds

        def fake_open(url, new):
            captured["url"] = url
            captured["new"] = new
            return True

        monkeypatch.setattr(dev, "ensure_local_server_running", fake_ensure_local_server_running)
        monkeypatch.setattr(dev.subprocess, "Popen", fake_popen)
        monkeypatch.setattr(dev.time, "sleep", fake_sleep)
        monkeypatch.setattr(dev.webbrowser, "open", fake_open)

        dev.open_local_inspector()

        assert captured["server_started"] is True
        assert captured["command"] == [
            "npx.cmd" if dev.os.name == "nt" else "npx",
            "--yes",
            "@modelcontextprotocol/inspector@0.22.0",
        ]
        assert captured["slept"] == 2
        assert captured["url"] == dev.LOCAL_INSPECTOR_URL
        assert captured["new"] == 1
        assert captured["waited"] is True
        assert server_process.terminated is True
