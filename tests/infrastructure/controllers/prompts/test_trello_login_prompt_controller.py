import pytest
from mcp.server import FastMCP

from mcp_server.infrastructure.controllers.prompts.trello_login_prompt_controller import TrelloLoginPromptController


@pytest.fixture
def prompt_server():
    server = FastMCP(name="test-prompts")
    TrelloLoginPromptController(server).register()
    return server


class TestRegistration:
    def test_registers_prompt(self, prompt_server):
        names = [p.name for p in prompt_server._prompt_manager.list_prompts()]
        assert "trello_login" in names


class TestTrelloLoginPrompt:
    @pytest.mark.anyio
    async def test_references_generate_auth_url_tool(self):
        controller = TrelloLoginPromptController.__new__(TrelloLoginPromptController)
        result = await controller.trello_login()
        assert "generate_trello_auth_url" in result

    @pytest.mark.anyio
    async def test_references_complete_auth_tool(self):
        controller = TrelloLoginPromptController.__new__(TrelloLoginPromptController)
        result = await controller.trello_login()
        assert "complete_trello_auth" in result

    @pytest.mark.anyio
    async def test_mentions_user_id(self):
        controller = TrelloLoginPromptController.__new__(TrelloLoginPromptController)
        result = await controller.trello_login()
        assert "user_id" in result
