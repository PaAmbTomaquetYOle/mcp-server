from __future__ import annotations

import threading

from mcp.server import FastMCP

from mcp_server.infrastructure.config.settings import McpServerSettings
from mcp_server.infrastructure.controllers.tools import PingToolController

_INTERNAL_TOKEN = object()


class ServerFactory:
    _instance: ServerFactory | None = None
    _lock: threading.Lock = threading.Lock()

    def __init__(
        self, settings: McpServerSettings, *, _token: object = None
    ) -> None:
        if _token is not _INTERNAL_TOKEN:
            raise TypeError(
                "ServerFactory is a singleton."
                " Use ServerFactory.get_instance() instead."
            )
        self._settings = settings

    @classmethod
    def get_instance(cls, settings: McpServerSettings) -> ServerFactory:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(settings, _token=_INTERNAL_TOKEN)
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        with cls._lock:
            cls._instance = None

    def create(self) -> FastMCP:
        server = FastMCP(
            name=self._settings.name,
            host=self._settings.host,
            port=self._settings.port,
            log_level=self._settings.log_level,
            debug=self._settings.debug,
        )
        self._register_tools(server)
        return server

    def _register_tools(self, server: FastMCP) -> None:
        PingToolController(server).register()
