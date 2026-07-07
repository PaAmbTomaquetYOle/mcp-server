import json
from unittest.mock import AsyncMock

import pytest

from mcp_server.application.services.dossier_generation_service import DossierGenerationService
from mcp_server.domain.search import SearchDocument
from mcp_server.infrastructure.dto.tools.dossier_schemas import GenerateDossierResponse


class _TextBlock:
    type = "text"

    def __init__(self, text: str) -> None:
        self.text = text

    def model_dump(self) -> dict:
        return {"type": "text", "text": self.text}


class _ToolUseBlock:
    type = "tool_use"

    def __init__(self, block_id: str, name: str, tool_input: dict) -> None:
        self.id = block_id
        self.name = name
        self.input = tool_input

    def model_dump(self) -> dict:
        return {"type": "tool_use", "id": self.id, "name": self.name, "input": self.input}


class _FakeMessage:
    def __init__(self, content: list, stop_reason: str) -> None:
        self.content = content
        self.stop_reason = stop_reason


def _make_client(responses: list[_FakeMessage]) -> AsyncMock:
    client = AsyncMock()
    client.messages = AsyncMock()
    client.messages.create = AsyncMock(side_effect=responses)
    return client


@pytest.fixture
def mock_backend_api():
    api = AsyncMock()
    api.search_dossiers = AsyncMock(return_value=[])
    return api


@pytest.fixture
def mock_search_connector():
    connector = AsyncMock()
    connector.test_search = AsyncMock(return_value=[])
    return connector


class TestDossierGenerationService:
    @pytest.mark.anyio
    async def test_final_answer_without_tool_use(self, mock_backend_api, mock_search_connector) -> None:
        final_json = json.dumps(
            {
                "summary": "Handover summary.",
                "sections": [
                    {
                        "section_type": "responsibilities",
                        "title": "Responsibilities",
                        "responsibilities": ["Lead the backend team"],
                    }
                ],
            }
        )
        client = _make_client([_FakeMessage([_TextBlock(final_json)], "end_turn")])
        service = DossierGenerationService(
            anthropic_client=client,
            model="test-model",
            backend_api=mock_backend_api,
            search_connector=mock_search_connector,
        )

        result = await service.generate("Q: What do you do?\nA: I lead backend.")

        assert isinstance(result, GenerateDossierResponse)
        assert result.summary == "Handover summary."
        assert len(result.sections) == 1
        assert result.sections[0].section_type == "responsibilities"
        assert result.sections[0].responsibilities == ["Lead the backend team"]

    @pytest.mark.anyio
    async def test_calls_search_prior_dossiers_tool(
        self, mock_backend_api, mock_search_connector
    ) -> None:
        mock_backend_api.search_dossiers.return_value = [{"id": "d1"}]
        final_json = json.dumps({"summary": "ok", "sections": []})
        responses = [
            _FakeMessage(
                [_ToolUseBlock("t1", "search_prior_dossiers", {"employee_name": "Jane"})],
                "tool_use",
            ),
            _FakeMessage([_TextBlock(final_json)], "end_turn"),
        ]
        service = DossierGenerationService(
            anthropic_client=_make_client(responses),
            model="test-model",
            backend_api=mock_backend_api,
            search_connector=mock_search_connector,
        )

        result = await service.generate("transcript")

        assert result.summary == "ok"
        mock_backend_api.search_dossiers.assert_awaited_once_with(
            employee_name="Jane", process_id=None
        )

    @pytest.mark.anyio
    async def test_calls_search_sops_tool(self, mock_backend_api, mock_search_connector) -> None:
        mock_search_connector.test_search.return_value = [
            SearchDocument(
                external_id="sop-1",
                title="Deploying",
                description="How to deploy",
                content="How to deploy the service",
                link="https://example.com/sop-1",
                author="Jane",
                tags=[],
                origin_channel="C1",
                date_updated="2026-01-01",
            )
        ]
        final_json = json.dumps({"summary": None, "sections": []})
        responses = [
            _FakeMessage([_ToolUseBlock("t1", "search_sops", {"query": "deploy"})], "tool_use"),
            _FakeMessage([_TextBlock(final_json)], "end_turn"),
        ]
        service = DossierGenerationService(
            anthropic_client=_make_client(responses),
            model="test-model",
            backend_api=mock_backend_api,
            search_connector=mock_search_connector,
        )

        result = await service.generate("transcript")

        assert result.summary is None
        mock_search_connector.test_search.assert_awaited_once_with("deploy")

    @pytest.mark.anyio
    async def test_unknown_tool_reports_error_result_and_continues(
        self, mock_backend_api, mock_search_connector
    ) -> None:
        final_json = json.dumps({"summary": None, "sections": []})
        responses = [
            _FakeMessage([_ToolUseBlock("t1", "bogus_tool", {})], "tool_use"),
            _FakeMessage([_TextBlock(final_json)], "end_turn"),
        ]
        service = DossierGenerationService(
            anthropic_client=_make_client(responses),
            model="test-model",
            backend_api=mock_backend_api,
            search_connector=mock_search_connector,
        )

        result = await service.generate("transcript")

        assert result.sections == []

    @pytest.mark.anyio
    async def test_raises_when_tool_iterations_exhausted(
        self, mock_backend_api, mock_search_connector
    ) -> None:
        always_tool_use = _FakeMessage(
            [_ToolUseBlock("t1", "search_prior_dossiers", {})], "tool_use"
        )
        service = DossierGenerationService(
            anthropic_client=_make_client([always_tool_use, always_tool_use]),
            model="test-model",
            backend_api=mock_backend_api,
            search_connector=mock_search_connector,
            max_tool_iterations=2,
        )

        with pytest.raises(RuntimeError, match="tool-call round trips"):
            await service.generate("transcript")

    @pytest.mark.anyio
    async def test_raises_on_malformed_json(self, mock_backend_api, mock_search_connector) -> None:
        service = DossierGenerationService(
            anthropic_client=_make_client([_FakeMessage([_TextBlock("not json")], "end_turn")]),
            model="test-model",
            backend_api=mock_backend_api,
            search_connector=mock_search_connector,
        )

        with pytest.raises(json.JSONDecodeError):
            await service.generate("transcript")

    @pytest.mark.anyio
    async def test_raises_on_invalid_section_shape(
        self, mock_backend_api, mock_search_connector
    ) -> None:
        final_json = json.dumps(
            {"summary": None, "sections": [{"section_type": "bogus", "title": "X"}]}
        )
        service = DossierGenerationService(
            anthropic_client=_make_client([_FakeMessage([_TextBlock(final_json)], "end_turn")]),
            model="test-model",
            backend_api=mock_backend_api,
            search_connector=mock_search_connector,
        )

        with pytest.raises(Exception):
            await service.generate("transcript")

    @pytest.mark.anyio
    async def test_strips_markdown_json_fence(self, mock_backend_api, mock_search_connector) -> None:
        text = '```json\n{"summary": null, "sections": []}\n```'
        service = DossierGenerationService(
            anthropic_client=_make_client([_FakeMessage([_TextBlock(text)], "end_turn")]),
            model="test-model",
            backend_api=mock_backend_api,
            search_connector=mock_search_connector,
        )

        result = await service.generate("transcript")

        assert result.summary is None
        assert result.sections == []
