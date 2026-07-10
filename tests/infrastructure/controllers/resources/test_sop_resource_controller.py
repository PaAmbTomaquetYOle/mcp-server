import json
from unittest.mock import AsyncMock

import pytest
from mcp.server import FastMCP
from mcp.server.fastmcp.exceptions import ResourceError

from mcp_server.domain import BackendApiException
from mcp_server.domain.search import SearchDocument
from mcp_server.infrastructure.controllers.resources.sop_resource_controller import SopResourceController
from mcp_server.infrastructure.dto import SopDetail, SopListResponse

_DOC = SearchDocument(
    external_id="1",
    title="Restart deploy pipeline",
    description="Restart deploy pipeline",
    content="Restart deploy pipeline",
    link="https://x/sops/1",
    author="U1",
    tags=["deploy"],
    origin_channel="C1",
    date_updated="2026-01-01",
)

_RAW_SOP = {
    "id": "1",
    "content": "Restart deploy pipeline",
    "author": "U1",
    "tags": ["deploy"],
    "origin_channel": "C1",
    "version": 2,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-02T00:00:00Z",
}


@pytest.fixture
def mock_service():
    service = AsyncMock()
    service.test_search = AsyncMock(return_value=[_DOC])
    service.handle_entity_details = AsyncMock(return_value=_RAW_SOP)
    return service


@pytest.fixture
def sop_server(mock_service):
    server = FastMCP(name="test-sop-resources")
    SopResourceController(server, mock_service).register()
    return server


class TestSopResourceRegistration:
    def test_registers_sop_list_resource(self, sop_server):
        resources = sop_server._resource_manager.list_resources()
        assert any(str(r.uri) == "sop://offboardme/sops" for r in resources)

    def test_registers_sop_detail_template(self, sop_server):
        templates = sop_server._resource_manager.list_templates()
        assert any(t.uri_template == "sop://offboardme/sops/{sop_id}" for t in templates)


class TestListSops:
    @pytest.mark.anyio
    async def test_returns_cached_sops(self, mock_service):
        controller = SopResourceController.__new__(SopResourceController)
        controller._SopResourceController__service = mock_service

        raw = await controller.list_sops()
        result = SopListResponse.model_validate(json.loads(raw))

        assert result.count == 1
        assert result.sops[0].id == "1"
        assert result.sops[0].title == "Restart deploy pipeline"
        assert result.sops[0].tags == ["deploy"]
        mock_service.test_search.assert_awaited_once_with("")


class TestGetSop:
    @pytest.mark.anyio
    async def test_returns_sop_detail(self, mock_service):
        controller = SopResourceController.__new__(SopResourceController)
        controller._SopResourceController__service = mock_service

        raw = await controller.get_sop("1")
        result = SopDetail.model_validate(json.loads(raw))

        assert result.id == "1"
        assert result.content == "Restart deploy pipeline"
        assert result.version == 2
        mock_service.handle_entity_details.assert_awaited_once_with({"id": "1"})

    @pytest.mark.anyio
    async def test_backend_error_raises_resource_error(self, mock_service):
        mock_service.handle_entity_details.side_effect = BackendApiException("SOP not found")
        controller = SopResourceController.__new__(SopResourceController)
        controller._SopResourceController__service = mock_service

        with pytest.raises(ResourceError):
            await controller.get_sop("missing")
