"""Entrypoint for the BrainTrust MCP server."""

from __future__ import annotations

import uvicorn

from mcp_server.infrastructure.config.settings import get_settings


def main() -> None:
    """Run the MCP server over HTTP."""

    settings = get_settings()
    uvicorn.run(
        "mcp_server.app:create_app",
        host=settings.host,
        port=settings.port,
        factory=True,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
