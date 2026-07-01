from unittest.mock import AsyncMock

import pytest
from mcp.server import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from mcp_server.domain import BackendApiException
from mcp_server.infrastructure.controllers.tools.get_dossier_controller import GetDossierToolController
from mcp_server.infrastructure.dto import GetDossierResponse
from tests.conftest import get_tool_names

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
    server = FastMCP(name="test-dossier")
    GetDossierToolController(server, mock_backend_api).register()
    return server


class TestGetDossierToolRegistration:
    def test_registers_get_dossier_tool(self, dossier_server):
        assert "get_dossier" in get_tool_names(dossier_server)


class TestGetDossier:
    @pytest.mark.anyio
    async def test_search_by_employee_name(self, mock_backend_api):
        controller = GetDossierToolController.__new__(GetDossierToolController)
        controller._GetDossierToolController__backend_api = mock_backend_api

        result = await controller.get_dossier(employee_name="Juan")

        assert isinstance(result, GetDossierResponse)
        assert result.count == 1
        assert result.results[0].employee_name == "Juan Perez"
        mock_backend_api.search_dossiers.assert_awaited_once_with(
            employee_name="Juan", process_id=None
        )

    @pytest.mark.anyio
    async def test_search_by_process_id(self, mock_backend_api):
        controller = GetDossierToolController.__new__(GetDossierToolController)
        controller._GetDossierToolController__backend_api = mock_backend_api

        result = await controller.get_dossier(process_id="p1")

        assert result.count == 1
        mock_backend_api.search_dossiers.assert_awaited_once_with(
            employee_name=None, process_id="p1"
        )

    @pytest.mark.anyio
    async def test_no_filters_raises_tool_error(self, mock_backend_api):
        controller = GetDossierToolController.__new__(GetDossierToolController)
        controller._GetDossierToolController__backend_api = mock_backend_api

        with pytest.raises(ToolError, match="employee_name.*process_id"):
            await controller.get_dossier()

    @pytest.mark.anyio
    async def test_backend_error_raises_tool_error(self, mock_backend_api):
        mock_backend_api.search_dossiers.side_effect = BackendApiException("backend down")
        controller = GetDossierToolController.__new__(GetDossierToolController)
        controller._GetDossierToolController__backend_api = mock_backend_api

        with pytest.raises(ToolError):
            await controller.get_dossier(employee_name="Juan")
