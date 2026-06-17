from __future__ import annotations

import subprocess
import sys

INSPECTOR_PACKAGE = "@modelcontextprotocol/inspector"


def build_inspector_command(extra_args: list[str] | None = None) -> list[str]:
    command = ["npx", "--yes", INSPECTOR_PACKAGE]
    if extra_args:
        command.extend(extra_args)
    return command


def main() -> None:
    try:
        subprocess.run(build_inspector_command(sys.argv[1:]), check=True)
    except FileNotFoundError as exc:
        raise RuntimeError(
            "npx is required to run the MCP Inspector. "
            "Install Node.js/npm and try again."
        ) from exc


if __name__ == "__main__":
    main()
