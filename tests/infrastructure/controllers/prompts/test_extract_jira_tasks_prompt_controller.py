import pytest
from mcp.server import FastMCP

from mcp_server.infrastructure.controllers.prompts.extract_jira_tasks_prompt_controller import (
    ExtractJiraTasksPromptController,
)


@pytest.fixture
def prompt_server():
    server = FastMCP(name="test-prompts")
    ExtractJiraTasksPromptController(server).register()
    return server


class TestRegistration:
    def test_registers_prompt(self, prompt_server):
        names = [p.name for p in prompt_server._prompt_manager.list_prompts()]
        assert "extract_pending_jira_tasks" in names


class TestExtractPendingJiraTasks:
    @pytest.mark.anyio
    async def test_references_tool_name(self):
        controller = ExtractJiraTasksPromptController.__new__(ExtractJiraTasksPromptController)
        result = await controller.extract_pending_jira_tasks(assignee="john")
        assert "get_pending_jira_issues" in result

    @pytest.mark.anyio
    async def test_includes_assignee(self):
        controller = ExtractJiraTasksPromptController.__new__(ExtractJiraTasksPromptController)
        result = await controller.extract_pending_jira_tasks(assignee="john")
        assert "john" in result

    @pytest.mark.anyio
    async def test_explains_auth_recovery_tools(self):
        controller = ExtractJiraTasksPromptController.__new__(ExtractJiraTasksPromptController)
        result = await controller.extract_pending_jira_tasks(assignee="john")
        assert "generate_jira_auth_url" in result
        assert "complete_jira_auth" in result

    @pytest.mark.anyio
    async def test_explains_auth_recovery_sequence(self):
        controller = ExtractJiraTasksPromptController.__new__(ExtractJiraTasksPromptController)
        result = await controller.extract_pending_jira_tasks(assignee="john")
        assert "not authenticated" in result
        assert "retry" in result.lower()
