from __future__ import annotations

import threading

from mcp.server import FastMCP

from mcp_server.application.ports import ITokenStoragePort
from mcp_server.application.services import CollaborationToolIntegrationService
from mcp_server.infrastructure.adapters import JiraAdapter, SqliteTokenStorage, TrelloAdapter
from mcp_server.infrastructure.config.settings import McpServerSettings
from mcp_server.infrastructure.controllers.tools import (
    ExtractJiraTasksToolController,
    ExtractTrelloTasksToolController,
    PingToolController,
)

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
    
    def _create_token_storage(self) -> ITokenStoragePort:
        return SqliteTokenStorage(db_path=self._settings.token_db_path)

    def _create_jira_adapter(self) -> JiraAdapter:
        return JiraAdapter(
            server_url=self._settings.jira_server_url,
            client_id=self._settings.jira_client_id,
            client_secret=self._settings.jira_client_secret,
            token_storage_port=self._create_token_storage(),
        )

    def _create_trello_adapter(self) -> TrelloAdapter:
        return TrelloAdapter(
            token_storage_port=self._create_token_storage(),
            api_key=self._settings.trello_api_key,
            api_secret=self._settings.trello_api_secret,
        )

    def _create_jira_service(self) -> CollaborationToolIntegrationService:
        jira_adapter = self._create_jira_adapter()
        jira_service = CollaborationToolIntegrationService(jira_adapter)
        return jira_service

    def _create_trello_service(self) -> CollaborationToolIntegrationService:
        trello_adapter = self._create_trello_adapter()
        trello_service = CollaborationToolIntegrationService(trello_adapter)
        return trello_service

    def _register_tools(self, server: FastMCP) -> None:
        PingToolController(server).register()
        
        jira_service = self._create_jira_service()
        ExtractJiraTasksToolController(server, jira_service).register()

        trello_service = self._create_trello_service()
        ExtractTrelloTasksToolController(server, trello_service).register()
