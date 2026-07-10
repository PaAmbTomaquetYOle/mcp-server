"""ASGI application factory for the BrainTrust MCP server."""

from __future__ import annotations

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from mcp_server.application.services.catalog import create_mcp_server
from mcp_server.infrastructure.config.settings import get_settings


async def health(_: Request) -> JSONResponse:
    """Return a basic liveness payload."""

    return JSONResponse({"status": "ok", "service": "mcp-server", "mode": "mcp-http"})


def create_app() -> Starlette:
    """Create the combined health + MCP ASGI application."""

    settings = get_settings()
    mcp_server = create_mcp_server(settings)
    return Starlette(
        debug=False,
        routes=[
            Route("/health", endpoint=health),
            Mount("/", app=mcp_server.streamable_http_app()),
        ],
        lifespan=lambda app: mcp_server.session_manager.run(),
    )
