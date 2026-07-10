from unittest.mock import AsyncMock

import pytest
from mcp.server import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from mcp_server.domain import PersonNotFoundException
from mcp_server.infrastructure.controllers.tools.knowledge_graph_controller import KnowledgeGraphToolController
from mcp_server.infrastructure.dto import AddInteractionResponse, KnowledgeMapResponse, QueryExpertsResponse
from tests.conftest import get_tool_names

_SAMPLE_EXPERT = {
    "person": {"person_id": "U1", "name": "Alice", "department": "SRE"},
    "topic": "kubernetes",
    "score": 3.0,
}
_SAMPLE_PROFILE = {
    "person": {"person_id": "U1", "name": "Alice", "department": "SRE"},
    "topics": [{"name": "kubernetes", "description": None}],
    "documents": [{"document_id": "D1", "title": "Runbook", "url": None, "source": "confluence"}],
}


@pytest.fixture
def mock_service():
    service = AsyncMock()
    service.query_experts = AsyncMock(return_value=[_SAMPLE_EXPERT])
    service.add_interaction = AsyncMock(return_value={"event_id": "e1", "status": "published"})
    service.get_knowledge_map = AsyncMock(return_value=_SAMPLE_PROFILE)
    return service


@pytest.fixture
def kg_server(mock_service):
    server = FastMCP(name="test-kg")
    KnowledgeGraphToolController(server, mock_service).register()
    return server


class TestKnowledgeGraphToolRegistration:
    def test_registers_all_three_tools(self, kg_server):
        tool_names = get_tool_names(kg_server)
        assert "query_experts" in tool_names
        assert "add_interaction" in tool_names
        assert "get_knowledge_map" in tool_names


class TestQueryExperts:
    @pytest.mark.anyio
    async def test_returns_matching_experts(self, mock_service):
        controller = KnowledgeGraphToolController.__new__(KnowledgeGraphToolController)
        controller._KnowledgeGraphToolController__service = mock_service

        result = await controller.query_experts("kubernetes", limit=5)

        assert isinstance(result, QueryExpertsResponse)
        assert result.count == 1
        assert result.experts[0].person.name == "Alice"
        mock_service.query_experts.assert_awaited_once_with("kubernetes", limit=5)


class TestAddInteraction:
    @pytest.mark.anyio
    async def test_registers_interaction(self, mock_service):
        controller = KnowledgeGraphToolController.__new__(KnowledgeGraphToolController)
        controller._KnowledgeGraphToolController__service = mock_service

        result = await controller.add_interaction(
            person_id="U1", person_name="Alice", topic_name="kubernetes", interaction_type="knows"
        )

        assert isinstance(result, AddInteractionResponse)
        assert result.event_id == "e1"
        assert result.status == "published"
        mock_service.add_interaction.assert_awaited_once_with(
            person_id="U1",
            person_name="Alice",
            topic_name="kubernetes",
            interaction_type="knows",
            department=None,
            topic_description=None,
        )


class TestGetKnowledgeMap:
    @pytest.mark.anyio
    async def test_returns_knowledge_map(self, mock_service):
        controller = KnowledgeGraphToolController.__new__(KnowledgeGraphToolController)
        controller._KnowledgeGraphToolController__service = mock_service

        result = await controller.get_knowledge_map("U1")

        assert isinstance(result, KnowledgeMapResponse)
        assert result.person.name == "Alice"
        assert result.topics[0].name == "kubernetes"
        assert result.documents[0].document_id == "D1"

    @pytest.mark.anyio
    async def test_person_not_found_raises_tool_error(self, mock_service):
        mock_service.get_knowledge_map.side_effect = PersonNotFoundException("missing")
        controller = KnowledgeGraphToolController.__new__(KnowledgeGraphToolController)
        controller._KnowledgeGraphToolController__service = mock_service

        with pytest.raises(ToolError):
            await controller.get_knowledge_map("missing")
