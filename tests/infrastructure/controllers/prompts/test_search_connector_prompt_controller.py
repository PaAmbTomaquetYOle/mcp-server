import pytest
from mcp.server import FastMCP

from mcp_server.infrastructure.controllers.prompts.search_connector_prompt_controller import (
    SearchConnectorPromptController,
)


@pytest.fixture
def prompt_server():
    server = FastMCP(name="test-prompts")
    SearchConnectorPromptController(server).register()
    return server


class TestRegistration:
    def test_registers_prompt(self, prompt_server):
        names = [p.name for p in prompt_server._prompt_manager.list_prompts()]
        assert "manage_search_connector" in names


class TestManageSearchConnectorPrompt:
    @pytest.mark.anyio
    async def test_references_status_tool(self):
        controller = SearchConnectorPromptController.__new__(SearchConnectorPromptController)
        result = await controller.manage_search_connector()
        assert "search_connector_status" in result

    @pytest.mark.anyio
    async def test_references_refresh_tool(self):
        controller = SearchConnectorPromptController.__new__(SearchConnectorPromptController)
        result = await controller.manage_search_connector()
        assert "refresh_search_index" in result

    @pytest.mark.anyio
    async def test_references_test_search_tool(self):
        controller = SearchConnectorPromptController.__new__(SearchConnectorPromptController)
        result = await controller.manage_search_connector()
        assert "test_search_query" in result
