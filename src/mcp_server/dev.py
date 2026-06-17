from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import webbrowser

INSPECTOR_PACKAGE = "@modelcontextprotocol/inspector@0.22.0"
INSPECTOR_IMAGE = "ghcr.io/modelcontextprotocol/inspector:latest"
NPX_COMMAND = "npx.cmd" if os.name == "nt" else "npx"
SERVER_COMMAND = [sys.executable, "-m", "mcp_server.main"]
LOCAL_SERVER_URL = "http://localhost:8000/mcp"
LOCAL_INSPECTOR_URL = (
    "http://localhost:6274/?transport=streamable-http&serverUrl="
    f"{LOCAL_SERVER_URL}"
)
LOCAL_SERVER_HOST = "127.0.0.1"
LOCAL_SERVER_PORT = 8000
SERVER_STARTUP_TIMEOUT_SECONDS = 30


def build_npx_command(extra_args: list[str] | None = None) -> list[str]:
    command = [NPX_COMMAND, "--yes", INSPECTOR_PACKAGE]
    if extra_args:
        command.extend(extra_args)
    return command


def build_docker_command(extra_args: list[str] | None = None) -> list[str]:
    command = [
        "docker",
        "run",
        "--rm",
        "-p",
        "127.0.0.1:6274:6274",
        "-p",
        "127.0.0.1:6277:6277",
        "-e",
        "HOST=0.0.0.0",
        "-e",
        "MCP_AUTO_OPEN_ENABLED=false",
        INSPECTOR_IMAGE,
    ]
    if extra_args:
        command.extend(extra_args)
    return command


def build_server_command() -> list[str]:
    return SERVER_COMMAND.copy()


def is_port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) == 0


def wait_for_port(host: str, port: int, timeout_seconds: int) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if is_port_open(host, port):
            return
        time.sleep(0.25)
    raise RuntimeError(
        f"Timed out waiting for {host}:{port} to become available."
    )


def ensure_local_server_running() -> subprocess.Popen[str] | None:
    if is_port_open(LOCAL_SERVER_HOST, LOCAL_SERVER_PORT):
        return None

    process = subprocess.Popen(build_server_command())
    try:
        wait_for_port(
            LOCAL_SERVER_HOST,
            LOCAL_SERVER_PORT,
            SERVER_STARTUP_TIMEOUT_SECONDS,
        )
        return process
    except Exception:
        process.terminate()
        raise


def open_local_inspector() -> None:
    server_process = None
    inspector_process = None
    try:
        server_process = ensure_local_server_running()
        inspector_process = subprocess.Popen(build_npx_command())
        time.sleep(2)
        webbrowser.open(LOCAL_INSPECTOR_URL, new=1)
        inspector_process.wait()
    except FileNotFoundError as exc:
        raise RuntimeError(
            "npx is required to run the MCP Inspector. "
            "Install Node.js/npm and try again."
        ) from exc
    except KeyboardInterrupt:
        if inspector_process and inspector_process.poll() is None:
            inspector_process.terminate()
        if server_process and server_process.poll() is None:
            server_process.terminate()
        raise
    finally:
        if inspector_process and inspector_process.poll() is None:
            inspector_process.terminate()
        if server_process and server_process.poll() is None:
            server_process.terminate()


def main() -> None:
    extra_args = sys.argv[1:]

    try:
        subprocess.run(build_npx_command(extra_args), check=True)
        return
    except FileNotFoundError:
        pass

    try:
        subprocess.run(build_docker_command(extra_args), check=True)
    except FileNotFoundError as exc:
        raise RuntimeError(
            "Neither npx nor docker was found. Install Node.js/npm or Docker Desktop "
            "to run the MCP Inspector."
        ) from exc


if __name__ == "__main__":
    main()
