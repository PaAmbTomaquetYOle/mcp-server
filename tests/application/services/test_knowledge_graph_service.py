from unittest.mock import ANY, AsyncMock

import pytest

from mcp_server.application.services.knowledge_graph_service import KnowledgeGraphService


@pytest.fixture
def mock_kg_port():
    port = AsyncMock()
    port.search_experts = AsyncMock(return_value=[{"person": {"person_id": "U1"}, "topic": "k8s", "score": 3.0}])
    port.get_person_knowledge = AsyncMock(return_value={"person": {"person_id": "U1"}, "topics": [], "documents": []})
    return port


@pytest.fixture
def mock_event_publisher():
    publisher = AsyncMock()
    publisher.publish = AsyncMock()
    return publisher


@pytest.fixture
def service(mock_kg_port, mock_event_publisher):
    return KnowledgeGraphService(kg_port=mock_kg_port, event_publisher=mock_event_publisher)


class TestQueryExperts:
    @pytest.mark.anyio
    async def test_delegates_to_port(self, service, mock_kg_port):
        result = await service.query_experts("kubernetes", limit=5)

        assert result == [{"person": {"person_id": "U1"}, "topic": "k8s", "score": 3.0}]
        mock_kg_port.search_experts.assert_awaited_once_with("kubernetes", limit=5)


class TestAddInteraction:
    @pytest.mark.anyio
    async def test_publishes_correct_envelope(self, service, mock_event_publisher):
        result = await service.add_interaction(
            person_id="U1",
            person_name="Alice",
            topic_name="kubernetes",
            interaction_type="knows",
            department="SRE",
            topic_description="Container orchestration",
        )

        assert "event_id" in result
        assert result["status"] == "published"
        mock_event_publisher.publish.assert_awaited_once_with(
            "slack-agent.knowledge_graph.interaction_registered",
            {
                "event_id": result["event_id"],
                "event_type": "knowledge_graph.interaction_registered",
                "occurred_at": ANY,
                "payload": {
                    "person_id": "U1",
                    "person_name": "Alice",
                    "topic_name": "kubernetes",
                    "interaction_type": "knows",
                    "department": "SRE",
                    "topic_description": "Container orchestration",
                },
            },
        )

    @pytest.mark.anyio
    async def test_event_id_is_unique_per_call(self, service):
        first = await service.add_interaction(
            person_id="U1", person_name="Alice", topic_name="kubernetes", interaction_type="knows"
        )
        second = await service.add_interaction(
            person_id="U1", person_name="Alice", topic_name="kubernetes", interaction_type="knows"
        )

        assert first["event_id"] != second["event_id"]


class TestGetKnowledgeMap:
    @pytest.mark.anyio
    async def test_delegates_to_port(self, service, mock_kg_port):
        result = await service.get_knowledge_map("U1")

        assert result == {"person": {"person_id": "U1"}, "topics": [], "documents": []}
        mock_kg_port.get_person_knowledge.assert_awaited_once_with("U1")
