import json
from unittest.mock import AsyncMock

import pytest
from mcp.server import FastMCP
from mcp.server.fastmcp.exceptions import ResourceError

from mcp_server.domain import BackendApiException
from mcp_server.infrastructure.controllers.resources.dossier_resource_controller import DossierResourceController
from mcp_server.infrastructure.dto import DossierSearchResult

_SAMPLE_DOSSIER = {
    "id": "d1",
    "process_id": "p1",
    "state": "approved",
    "created_at": "2026-01-01T00:00:00Z",
    "summary": "Handover summary",
    "sections": [],
    "employee_id": "U12345",
    "manager_id": "U67890",
    "employee_name": "Juan Perez",
    "manager_name": "Ana Gomez",
}


@pytest.fixture
def mock_backend_api():
    api = AsyncMock()
    api.search_dossiers = AsyncMock(return_value=[_SAMPLE_DOSSIER])
    return api


@pytest.fixture
def dossier_server(mock_backend_api):
    server = FastMCP(name="test-dossier-resources")
    DossierResourceController(server, mock_backend_api).register()
    return server


class TestDossierResourceRegistration:
    def test_registers_dossier_detail_template(self, dossier_server):
        templates = dossier_server._resource_manager.list_templates()
        assert any(t.uri_template == "dossier://offboardme/dossiers/{process_id}" for t in templates)


class TestGetDossier:
    @pytest.mark.anyio
    async def test_returns_dossier_by_process_id(self, mock_backend_api):
        controller = DossierResourceController.__new__(DossierResourceController)
        controller._DossierResourceController__backend_api = mock_backend_api

        raw = await controller.get_dossier("p1")
        result = DossierSearchResult.model_validate(json.loads(raw))

        assert result.process_id == "p1"
        assert result.employee_name == "Juan Perez"
        mock_backend_api.search_dossiers.assert_awaited_once_with(process_id="p1")

    @pytest.mark.anyio
    async def test_not_found_raises_resource_error(self, mock_backend_api):
        mock_backend_api.search_dossiers.return_value = []
        controller = DossierResourceController.__new__(DossierResourceController)
        controller._DossierResourceController__backend_api = mock_backend_api

        with pytest.raises(ResourceError):
            await controller.get_dossier("missing")

    @pytest.mark.anyio
    async def test_backend_error_raises_resource_error(self, mock_backend_api):
        mock_backend_api.search_dossiers.side_effect = BackendApiException("backend down")
        controller = DossierResourceController.__new__(DossierResourceController)
        controller._DossierResourceController__backend_api = mock_backend_api

        with pytest.raises(ResourceError):
            await controller.get_dossier("p1")
