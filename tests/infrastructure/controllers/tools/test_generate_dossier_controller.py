from unittest.mock import AsyncMock

import pytest
from mcp.server import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from mcp_server.infrastructure.controllers.tools.generate_dossier_controller import (
    GenerateDossierToolController,
)
from mcp_server.infrastructure.dto import GenerateDossierResponse
from tests.conftest import get_tool_names


@pytest.fixture
def mock_service():
    service = AsyncMock()
    service.generate = AsyncMock(
        return_value=GenerateDossierResponse(summary="ok", sections=[])
    )
    return service


@pytest.fixture
def dossier_server(mock_service):
    server = FastMCP(name="test-generate-dossier")
    GenerateDossierToolController(server, mock_service).register()
    return server


class TestGenerateDossierToolRegistration:
    def test_registers_generate_dossier_tool(self, dossier_server):
        assert "generate_dossier" in get_tool_names(dossier_server)


class TestGenerateDossier:
    @pytest.mark.anyio
    async def test_delegates_to_service_with_default_offboarding_scope(self, mock_service) -> None:
        controller = GenerateDossierToolController.__new__(GenerateDossierToolController)
        controller._GenerateDossierToolController__service = mock_service

        result = await controller.generate_dossier("Q: ...\nA: ...")

        assert isinstance(result, GenerateDossierResponse)
        assert result.summary == "ok"
        mock_service.generate.assert_awaited_once_with("Q: ...\nA: ...", "offboarding")

    @pytest.mark.anyio
    async def test_delegates_to_service_with_monthly_scope(self, mock_service) -> None:
        controller = GenerateDossierToolController.__new__(GenerateDossierToolController)
        controller._GenerateDossierToolController__service = mock_service

        await controller.generate_dossier("Q: ...\nA: ...", review_scope="monthly")

        mock_service.generate.assert_awaited_once_with("Q: ...\nA: ...", "monthly")

    @pytest.mark.anyio
    async def test_delegates_to_service_with_annual_scope(self, mock_service) -> None:
        controller = GenerateDossierToolController.__new__(GenerateDossierToolController)
        controller._GenerateDossierToolController__service = mock_service

        await controller.generate_dossier("Q: ...\nA: ...", review_scope="annual")

        mock_service.generate.assert_awaited_once_with("Q: ...\nA: ...", "annual")

    @pytest.mark.anyio
    async def test_empty_transcript_raises_tool_error(self, mock_service) -> None:
        controller = GenerateDossierToolController.__new__(GenerateDossierToolController)
        controller._GenerateDossierToolController__service = mock_service

        with pytest.raises(ToolError, match="interview_transcript"):
            await controller.generate_dossier("   ")

    @pytest.mark.anyio
    async def test_service_error_raises_tool_error(self, mock_service) -> None:
        mock_service.generate.side_effect = RuntimeError("LLM did not produce a final dossier")
        controller = GenerateDossierToolController.__new__(GenerateDossierToolController)
        controller._GenerateDossierToolController__service = mock_service

        with pytest.raises(ToolError):
            await controller.generate_dossier("Q: ...\nA: ...")
