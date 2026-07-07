import pytest
from mcp.server import FastMCP

from mcp_server.infrastructure.controllers.prompts.extract_trello_tasks_prompt_controller import (
    ExtractTrelloTasksPromptController,
)


@pytest.fixture
def prompt_server():
    server = FastMCP(name="test-prompts")
    ExtractTrelloTasksPromptController(server).register()
    return server


class TestRegistration:
    def test_registers_prompt(self, prompt_server):
        names = [p.name for p in prompt_server._prompt_manager.list_prompts()]
        assert "extract_pending_trello_tasks" in names


class TestExtractPendingTrelloTasks:
    @pytest.mark.anyio
    async def test_references_tool_name(self):
        controller = ExtractTrelloTasksPromptController.__new__(ExtractTrelloTasksPromptController)
        result = await controller.extract_pending_trello_tasks(assignee="jane")
        assert "get_pending_trello_cards" in result

    @pytest.mark.anyio
    async def test_includes_assignee(self):
        controller = ExtractTrelloTasksPromptController.__new__(ExtractTrelloTasksPromptController)
        result = await controller.extract_pending_trello_tasks(assignee="jane")
        assert "jane" in result

    @pytest.mark.anyio
    async def test_explains_auth_recovery_tools(self):
        controller = ExtractTrelloTasksPromptController.__new__(ExtractTrelloTasksPromptController)
        result = await controller.extract_pending_trello_tasks(assignee="jane")
        assert "generate_trello_auth_url" in result
        assert "complete_trello_auth" in result

    @pytest.mark.anyio
    async def test_explains_auth_recovery_sequence(self):
        controller = ExtractTrelloTasksPromptController.__new__(ExtractTrelloTasksPromptController)
        result = await controller.extract_pending_trello_tasks(assignee="jane")
        assert "not authenticated" in result
        assert "retry" in result.lower()
