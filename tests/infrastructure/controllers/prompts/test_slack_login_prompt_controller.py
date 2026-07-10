import pytest
from mcp.server import FastMCP

from mcp_server.infrastructure.controllers.prompts.slack_login_prompt_controller import SlackLoginPromptController


@pytest.fixture
def prompt_server():
    server = FastMCP(name="test-prompts")
    SlackLoginPromptController(server).register()
    return server


class TestRegistration:
    def test_registers_prompt(self, prompt_server):
        names = [p.name for p in prompt_server._prompt_manager.list_prompts()]
        assert "slack_login" in names


class TestSlackLoginPrompt:
    @pytest.mark.anyio
    async def test_references_generate_auth_url_tool(self):
        controller = SlackLoginPromptController.__new__(SlackLoginPromptController)
        result = await controller.slack_login()
        assert "generate_slack_auth_url" in result

    @pytest.mark.anyio
    async def test_references_complete_auth_tool(self):
        controller = SlackLoginPromptController.__new__(SlackLoginPromptController)
        result = await controller.slack_login()
        assert "complete_slack_auth" in result

    @pytest.mark.anyio
    async def test_references_search_workspace_tool(self):
        controller = SlackLoginPromptController.__new__(SlackLoginPromptController)
        result = await controller.slack_login()
        assert "search_slack_workspace" in result
