import pytest
from mcp.server import FastMCP

from mcp_server.infrastructure.controllers.prompts.jira_login_prompt_controller import JiraLoginPromptController


@pytest.fixture
def prompt_server():
    server = FastMCP(name="test-prompts")
    JiraLoginPromptController(server).register()
    return server


class TestRegistration:
    def test_registers_prompt(self, prompt_server):
        names = [p.name for p in prompt_server._prompt_manager.list_prompts()]
        assert "jira_login" in names


class TestJiraLoginPrompt:
    @pytest.mark.anyio
    async def test_references_generate_auth_url_tool(self):
        controller = JiraLoginPromptController.__new__(JiraLoginPromptController)
        result = await controller.jira_login()
        assert "generate_jira_auth_url" in result

    @pytest.mark.anyio
    async def test_references_complete_auth_tool(self):
        controller = JiraLoginPromptController.__new__(JiraLoginPromptController)
        result = await controller.jira_login()
        assert "complete_jira_auth" in result

    @pytest.mark.anyio
    async def test_mentions_email_as_user_id(self):
        controller = JiraLoginPromptController.__new__(JiraLoginPromptController)
        result = await controller.jira_login()
        assert "email" in result
        assert "user_id" in result
