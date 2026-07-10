from unittest.mock import AsyncMock

import pytest

from mcp_server.domain import KnowledgeGraphApiException, PersonNotFoundException
from mcp_server.infrastructure.adapters.knowledge_graph_api import KnowledgeGraphApiAdapter


class _StubTokenProvider:
    async def get_access_token(self) -> str:
        return "test-token"


def _mock_response(json_data, status_code=200):
    response = AsyncMock()
    response.status_code = status_code
    response.json = lambda: json_data
    response.raise_for_status = lambda: None
    return response


@pytest.fixture
def client():
    return AsyncMock()


@pytest.fixture
def adapter(client):
    return KnowledgeGraphApiAdapter(
        base_url="http://backend/api/v1",
        token_provider=_StubTokenProvider(),
        client=client,
    )


class TestSearchExperts:
    @pytest.mark.anyio
    async def test_search_experts_sends_bearer_token(self, adapter, client):
        experts = [{"person": {"person_id": "U1", "name": "Alice", "department": None}, "topic": "k8s", "score": 3.0}]
        client.get = AsyncMock(return_value=_mock_response(experts))

        result = await adapter.search_experts("kubernetes", limit=5)

        assert result == experts
        client.get.assert_awaited_once()
        called_url = client.get.await_args.args[0]
        called_headers = client.get.await_args.kwargs["headers"]
        assert "http://backend/api/v1/knowledge-graph/experts" in called_url
        assert "topic=kubernetes" in called_url
        assert "limit=5" in called_url
        assert called_headers == {"Authorization": "Bearer test-token"}

    @pytest.mark.anyio
    async def test_wraps_http_errors(self, adapter, client):
        from httpx2 import HTTPStatusError

        error_response = _mock_response({}, status_code=500)

        def _raise():
            raise HTTPStatusError("error", request=None, response=error_response)

        error_response.raise_for_status = _raise
        client.get = AsyncMock(return_value=error_response)

        with pytest.raises(KnowledgeGraphApiException):
            await adapter.search_experts("kubernetes")


class TestGetPersonKnowledge:
    @pytest.mark.anyio
    async def test_returns_person_knowledge_profile(self, adapter, client):
        profile = {"person": {"person_id": "U1", "name": "Alice", "department": "SRE"}, "topics": [], "documents": []}
        client.get = AsyncMock(return_value=_mock_response(profile))

        result = await adapter.get_person_knowledge("U1")

        assert result == profile
        client.get.assert_awaited_once_with(
            "http://backend/api/v1/knowledge-graph/persons/U1",
            headers={"Authorization": "Bearer test-token"},
        )

    @pytest.mark.anyio
    async def test_404_raises_person_not_found(self, adapter, client):
        from httpx2 import HTTPStatusError

        error_response = _mock_response({}, status_code=404)

        def _raise():
            raise HTTPStatusError("not found", request=None, response=error_response)

        error_response.raise_for_status = _raise
        client.get = AsyncMock(return_value=error_response)

        with pytest.raises(PersonNotFoundException):
            await adapter.get_person_knowledge("missing")

    @pytest.mark.anyio
    async def test_other_http_errors_raise_knowledge_graph_api_exception(self, adapter, client):
        from httpx2 import HTTPStatusError

        error_response = _mock_response({}, status_code=500)

        def _raise():
            raise HTTPStatusError("error", request=None, response=error_response)

        error_response.raise_for_status = _raise
        client.get = AsyncMock(return_value=error_response)

        with pytest.raises(KnowledgeGraphApiException):
            await adapter.get_person_knowledge("U1")

    @pytest.mark.anyio
    async def test_network_error_raises_knowledge_graph_api_exception(self, adapter, client):
        client.get = AsyncMock(side_effect=ConnectionError("network down"))

        with pytest.raises(KnowledgeGraphApiException):
            await adapter.get_person_knowledge("U1")
