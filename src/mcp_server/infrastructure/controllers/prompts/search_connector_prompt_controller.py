from mcp.server.fastmcp.prompts.base import Prompt

from mcp_server.infrastructure.controllers import BaseController


class SearchConnectorPromptController(BaseController):
    """Prompt controller that guides an agent through managing the Slack search connector."""

    def register(self) -> None:
        self._server.add_prompt(
            Prompt(
                name="manage_search_connector",
                title="Manage Slack Search Connector",
                description="Guide the user through checking and maintaining the Slack Enterprise "
                "Search connector for SOPs.",
                fn=self.manage_search_connector,
                arguments=[],
                context_kwarg=None,
            )
        )

    @staticmethod
    async def manage_search_connector() -> str:
        return (
            "You are the Slack Enterprise Search connector assistant. Your goal is to help the "
            "user verify and maintain the connector that makes SOPs searchable from Slack.\n\n"
            "Available tools:\n\n"
            "1. `search_connector_status` — check whether the backend is reachable and whether "
            "the SOP cache is stale. Use this first to diagnose issues.\n"
            "2. `refresh_search_index` — force a full refresh of the SOP cache from the backend. "
            "Use this if the status shows the cache is stale or missing recent SOPs.\n"
            "3. `test_search_query` — run a search against the cached SOPs without going through "
            "Slack, to verify a given query returns the expected results.\n"
            "4. `get_search_analytics` — report cache hit/miss statistics to gauge how well the "
            "connector is serving real searches.\n\n"
            "Typical flow: call `search_connector_status`; if stale or empty, call "
            "`refresh_search_index`; then use `test_search_query` with a sample query to confirm "
            "SOPs are being found correctly."
        )
