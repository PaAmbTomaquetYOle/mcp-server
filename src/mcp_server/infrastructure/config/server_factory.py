from __future__ import annotations

import threading

from anthropic import AsyncAnthropic
from httpx2 import AsyncClient
from mcp.server import FastMCP

from mcp_server.application.ports import (
    IBackendApiPort,
    IBackendTokenProvider,
    IEventPublisherPort,
    IKnowledgeGraphPort,
    ISlackApiPort,
    ISopCachePort,
    ITokenStoragePort,
)
from mcp_server.application.service_interfaces import (
    IDossierGenerationService,
    IKnowledgeGraphService,
    ISearchConnectorService,
)
from mcp_server.application.services import (
    CollaborationToolIntegrationService,
    DossierGenerationService,
    JiraAuthService,
    KnowledgeGraphService,
    SearchConnectorService,
    SlackAuthService,
    SlackWorkspaceSearchService,
    TrelloAuthService,
)
from mcp_server.domain.search import RelevanceScorer, SynonymExpander, TokenNormalizer
from mcp_server.infrastructure.adapters import (
    BackendApiAdapter,
    BackendTokenClient,
    InMemorySopCacheAdapter,
    JiraAdapter,
    JiraAuthAdapter,
    KafkaEventPublisherAdapter,
    KnowledgeGraphApiAdapter,
    SlackApiAdapter,
    SlackAuthAdapter,
    SlackWorkspaceSearchAdapter,
    SqliteTokenStorage,
    TokenEncryptor,
    TrelloAdapter,
    TrelloAuthAdapter,
)
from mcp_server.infrastructure.config.settings import McpServerSettings
from mcp_server.infrastructure.controllers.prompts import (
    ExtractJiraTasksPromptController,
    ExtractTrelloTasksPromptController,
    JiraLoginPromptController,
    SearchConnectorPromptController,
    SlackLoginPromptController,
    TrelloLoginPromptController,
)
from mcp_server.infrastructure.controllers.resources import (
    DossierResourceController,
    KnowledgeGraphResourceController,
    SopResourceController,
)
from mcp_server.infrastructure.controllers.routes import (
    OAuthCallbackController,
    SlackEventsRouteController,
    SlackOAuthCallbackController,
)
from mcp_server.infrastructure.controllers.tools import (
    ExtractJiraTasksToolController,
    ExtractTrelloTasksToolController,
    GenerateDossierToolController,
    GetDossierToolController,
    JiraAuthToolController,
    KnowledgeGraphToolController,
    PingToolController,
    SearchConnectorToolController,
    SlackAuthToolController,
    SlackWorkspaceSearchToolController,
    TrelloAuthToolController,
)

_INTERNAL_TOKEN = object()


class ServerFactory:
    _instance: ServerFactory | None = None
    _lock: threading.Lock = threading.Lock()

    def __init__(
        self, settings: McpServerSettings, *, _token: object = None
    ) -> None:
        """
        Initialize the ServerFactory with the provided settings.
        This constructor is private and should not be called directly.
        Use ServerFactory.get_instance() to get the singleton instance.
        """
        if _token is not _INTERNAL_TOKEN:
            raise TypeError(
                "ServerFactory is a singleton."
                " Use ServerFactory.get_instance() instead."
            )
        self._settings = settings
        self._search_connector_service: ISearchConnectorService | None = None
        self._backend_api_adapter: IBackendApiPort | None = None
        self._backend_http_client: AsyncClient | None = None
        self._backend_token_provider: IBackendTokenProvider | None = None
        self._knowledge_graph_adapter: IKnowledgeGraphPort | None = None
        self._event_publisher_adapter: IEventPublisherPort | None = None
        self._token_storage: ITokenStoragePort | None = None

    @classmethod
    def get_instance(cls, settings: McpServerSettings) -> ServerFactory:
        """
        Get an instance of the ServerFactory singleton.

        Args:
            settings (McpServerSettings): The application settings.

        Returns:
            ServerFactory instance.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(settings, _token=_INTERNAL_TOKEN)
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """
        Reset the singleton instance of ServerFactory.
        This method is primarily for testing purposes to allow re-initialization of the singleton.
        """
        with cls._lock:
            cls._instance = None

    def create(self) -> FastMCP:
        """
        Create and configure a FastMCP server instance with the necessary tools and prompts.

        Returns:
            FastMCP server instance.
        """
        server = FastMCP(
            name=self._settings.name,
            host=self._settings.host,
            port=self._settings.port,
            log_level=self._settings.log_level,
            debug=self._settings.debug,
        )
        self._register_tools(server)
        self._register_prompts(server)
        self._register_resources(server)
        self._register_routes(server)
        return server
    
    def _create_token_storage(self) -> ITokenStoragePort:
        """Return the singleton token storage, shared by all adapters/services that need it."""
        if self._token_storage is None:
            encryptor = TokenEncryptor(self._settings.token_encryption_key)
            self._token_storage = SqliteTokenStorage(
                db_path=self._settings.token_db_path,
                encryptor=encryptor,
            )
        return self._token_storage

    def _create_jira_adapter(self) -> JiraAdapter:
        return JiraAdapter(
            cloud_id=self._settings.jira_cloud_id,
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

    def _create_jira_auth_adapter(self) -> JiraAuthAdapter:
        return JiraAuthAdapter(
            token_storage_port=self._create_token_storage(),
            client_id=self._settings.jira_client_id,
            client_secret=self._settings.jira_client_secret,
            redirect_uri=self._settings.jira_redirect_uri,
        )

    def _create_trello_auth_adapter(self) -> TrelloAuthAdapter:
        return TrelloAuthAdapter(
            token_storage_port=self._create_token_storage(),
            api_key=self._settings.trello_api_key,
            app_name=self._settings.trello_app_name,
        )

    def _create_jira_auth_service(self) -> JiraAuthService:
        return JiraAuthService(self._create_jira_auth_adapter())

    def _create_jira_service(self) -> CollaborationToolIntegrationService:
        jira_adapter = self._create_jira_adapter()
        jira_service = CollaborationToolIntegrationService(jira_adapter)
        return jira_service

    def _create_trello_auth_service(self) -> TrelloAuthService:
        return TrelloAuthService(self._create_trello_auth_adapter())

    def _create_trello_service(self) -> CollaborationToolIntegrationService:
        trello_adapter = self._create_trello_adapter()
        trello_service = CollaborationToolIntegrationService(trello_adapter)
        return trello_service

    def _get_backend_http_client(self) -> AsyncClient:
        """Return the singleton HTTP client shared by all backend API adapters."""
        if self._backend_http_client is None:
            self._backend_http_client = AsyncClient()
        return self._backend_http_client

    def _get_backend_token_provider(self) -> IBackendTokenProvider:
        """Return the singleton token provider shared by all backend API adapters."""
        if self._backend_token_provider is None:
            self._backend_token_provider = BackendTokenClient(
                base_url=self._settings.backend_api_url,
                client_id=self._settings.backend_client_id,
                client_secret=self._settings.backend_client_secret,
                client=self._get_backend_http_client(),
            )
        return self._backend_token_provider

    def _create_backend_api_adapter(self) -> IBackendApiPort:
        """Return the singleton backend API adapter, sharing one HTTP client and token cache."""
        if self._backend_api_adapter is None:
            self._backend_api_adapter = BackendApiAdapter(
                base_url=self._settings.backend_api_url,
                token_provider=self._get_backend_token_provider(),
                client=self._get_backend_http_client(),
            )
        return self._backend_api_adapter

    def _create_knowledge_graph_adapter(self) -> IKnowledgeGraphPort:
        """Return the singleton Knowledge Graph adapter, sharing the backend HTTP client and token cache."""
        if self._knowledge_graph_adapter is None:
            self._knowledge_graph_adapter = KnowledgeGraphApiAdapter(
                base_url=self._settings.backend_api_url,
                token_provider=self._get_backend_token_provider(),
                client=self._get_backend_http_client(),
            )
        return self._knowledge_graph_adapter

    def _create_event_publisher_adapter(self) -> IEventPublisherPort:
        """Return the singleton Kafka event publisher, connecting lazily on first publish."""
        if self._event_publisher_adapter is None:
            self._event_publisher_adapter = KafkaEventPublisherAdapter(
                bootstrap_servers=self._settings.kafka_bootstrap_servers,
            )
        return self._event_publisher_adapter

    def _create_knowledge_graph_service(self) -> IKnowledgeGraphService:
        return KnowledgeGraphService(
            kg_port=self._create_knowledge_graph_adapter(),
            event_publisher=self._create_event_publisher_adapter(),
        )

    def _create_slack_api_adapter(self) -> ISlackApiPort:
        return SlackApiAdapter(bot_token=self._settings.slack_bot_token)

    def _create_slack_auth_adapter(self) -> SlackAuthAdapter:
        return SlackAuthAdapter(
            token_storage_port=self._create_token_storage(),
            client_id=self._settings.slack_client_id,
            client_secret=self._settings.slack_client_secret,
            redirect_uri=self._settings.slack_redirect_uri,
        )

    def _create_slack_auth_service(self) -> SlackAuthService:
        return SlackAuthService(self._create_slack_auth_adapter())

    def _create_slack_workspace_search_service(self) -> SlackWorkspaceSearchService:
        return SlackWorkspaceSearchService(
            token_storage=self._create_token_storage(),
            workspace_search_port=SlackWorkspaceSearchAdapter(),
        )

    def _create_sop_cache_adapter(self) -> ISopCachePort:
        normalizer = TokenNormalizer()
        scorer = RelevanceScorer(normalizer=normalizer, expander=SynonymExpander(normalizer))
        return InMemorySopCacheAdapter(ttl_seconds=self._settings.sop_cache_ttl_seconds, scorer=scorer)

    def _create_dossier_generation_service(self) -> IDossierGenerationService:
        return DossierGenerationService(
            anthropic_client=AsyncAnthropic(api_key=self._settings.anthropic_api_key),
            model=self._settings.anthropic_model,
            backend_api=self._create_backend_api_adapter(),
            search_connector=self.get_search_connector_service(),
            max_tool_iterations=self._settings.dossier_generation_max_tool_iterations,
            max_tokens=self._settings.dossier_generation_max_tokens,
            max_tokens_annual=self._settings.dossier_generation_max_tokens_annual,
        )

    def get_search_connector_service(self) -> ISearchConnectorService:
        """Return the singleton search connector service, shared by tools, routes, and the cache-refresh task."""
        if self._search_connector_service is None:
            self._search_connector_service = SearchConnectorService(
                backend_api=self._create_backend_api_adapter(),
                sop_cache=self._create_sop_cache_adapter(),
                sop_base_url=self._settings.sop_base_url,
            )
        return self._search_connector_service

    def _register_tools(self, server: FastMCP) -> None:
        PingToolController(server).register()

        jira_service = self._create_jira_service()
        ExtractJiraTasksToolController(server, jira_service).register()

        jira_auth_service = self._create_jira_auth_service()
        JiraAuthToolController(server, jira_auth_service).register()

        trello_service = self._create_trello_service()
        ExtractTrelloTasksToolController(server, trello_service).register()

        trello_auth_service = self._create_trello_auth_service()
        TrelloAuthToolController(server, trello_auth_service).register()

        backend_api_adapter = self._create_backend_api_adapter()
        GetDossierToolController(server, backend_api_adapter).register()

        dossier_generation_service = self._create_dossier_generation_service()
        GenerateDossierToolController(server, dossier_generation_service).register()

        search_connector_service = self.get_search_connector_service()
        SearchConnectorToolController(server, search_connector_service).register()

        slack_auth_service = self._create_slack_auth_service()
        SlackAuthToolController(server, slack_auth_service).register()

        slack_workspace_search_service = self._create_slack_workspace_search_service()
        SlackWorkspaceSearchToolController(server, slack_workspace_search_service).register()

        knowledge_graph_service = self._create_knowledge_graph_service()
        KnowledgeGraphToolController(server, knowledge_graph_service).register()

    def _register_prompts(self, server: FastMCP) -> None:
        ExtractJiraTasksPromptController(server).register()
        ExtractTrelloTasksPromptController(server).register()
        JiraLoginPromptController(server).register()
        TrelloLoginPromptController(server).register()
        SearchConnectorPromptController(server).register()
        SlackLoginPromptController(server).register()

    def _register_resources(self, server: FastMCP) -> None:
        search_connector_service = self.get_search_connector_service()
        SopResourceController(server, search_connector_service).register()

        backend_api_adapter = self._create_backend_api_adapter()
        DossierResourceController(server, backend_api_adapter).register()

        knowledge_graph_adapter = self._create_knowledge_graph_adapter()
        KnowledgeGraphResourceController(server, knowledge_graph_adapter).register()

    def _register_routes(self, server: FastMCP) -> None:
        jira_auth_service = self._create_jira_auth_service()
        OAuthCallbackController(server, jira_auth_service).register()

        search_connector_service = self.get_search_connector_service()
        slack_api_adapter = self._create_slack_api_adapter()
        SlackEventsRouteController(
            server, search_connector_service, slack_api_adapter, signing_secret=self._settings.slack_signing_secret
        ).register()

        slack_auth_service = self._create_slack_auth_service()
        SlackOAuthCallbackController(server, slack_auth_service).register()