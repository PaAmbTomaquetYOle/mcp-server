import json
from unittest.mock import AsyncMock

import pytest
from mcp.server import FastMCP
from mcp.server.fastmcp.exceptions import ResourceError

from mcp_server.domain import PersonNotFoundException
from mcp_server.infrastructure.controllers.resources.knowledge_graph_resource_controller import (
    KnowledgeGraphResourceController,
)
from mcp_server.infrastructure.dto import KnowledgeMapResponse, QueryExpertsResponse

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
def mock_kg_port():
    port = AsyncMock()
    port.search_experts = AsyncMock(return_value=[_SAMPLE_EXPERT])
    port.get_person_knowledge = AsyncMock(return_value=_SAMPLE_PROFILE)
    return port


@pytest.fixture
def kg_server(mock_kg_port):
    server = FastMCP(name="test-kg-resources")
    KnowledgeGraphResourceController(server, mock_kg_port).register()
    return server


class TestKnowledgeGraphResourceRegistration:
    def test_registers_experts_template(self, kg_server):
        templates = kg_server._resource_manager.list_templates()
        assert any(t.uri_template == "kg://offboardme/experts/{topic}" for t in templates)

    def test_registers_person_profile_template(self, kg_server):
        templates = kg_server._resource_manager.list_templates()
        assert any(t.uri_template == "kg://offboardme/persons/{person_id}/profile" for t in templates)


class TestGetExperts:
    @pytest.mark.anyio
    async def test_returns_matching_experts(self, mock_kg_port):
        controller = KnowledgeGraphResourceController.__new__(KnowledgeGraphResourceController)
        controller._KnowledgeGraphResourceController__kg_port = mock_kg_port

        raw = await controller.get_experts("kubernetes")
        result = QueryExpertsResponse.model_validate(json.loads(raw))

        assert result.count == 1
        assert result.experts[0].person.name == "Alice"
        mock_kg_port.search_experts.assert_awaited_once_with("kubernetes")


class TestGetPersonProfile:
    @pytest.mark.anyio
    async def test_returns_person_profile(self, mock_kg_port):
        controller = KnowledgeGraphResourceController.__new__(KnowledgeGraphResourceController)
        controller._KnowledgeGraphResourceController__kg_port = mock_kg_port

        raw = await controller.get_person_profile("U1")
        result = KnowledgeMapResponse.model_validate(json.loads(raw))

        assert result.person.name == "Alice"
        assert result.topics[0].name == "kubernetes"
        assert result.documents[0].document_id == "D1"

    @pytest.mark.anyio
    async def test_person_not_found_raises_resource_error(self, mock_kg_port):
        mock_kg_port.get_person_knowledge.side_effect = PersonNotFoundException("missing")
        controller = KnowledgeGraphResourceController.__new__(KnowledgeGraphResourceController)
        controller._KnowledgeGraphResourceController__kg_port = mock_kg_port

        with pytest.raises(ResourceError):
            await controller.get_person_profile("missing")
