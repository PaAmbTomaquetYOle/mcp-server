from mcp.server import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from mcp_server.application.service_interfaces.dossier_generation_service_interface import (
    IDossierGenerationService,
)
from mcp_server.infrastructure.controllers.base_controller import BaseController
from mcp_server.infrastructure.controllers.error_handler import tool_error_handler
from mcp_server.infrastructure.dto import GenerateDossierResponse


class GenerateDossierToolController(BaseController):
    """Controller for the tool that generates offboarding dossier content via an LLM."""

    __service: IDossierGenerationService

    def __init__(self, server: FastMCP, service: IDossierGenerationService) -> None:
        super().__init__(server)
        self.__service = service

    def register(self) -> None:
        self._server.add_tool(
            self.generate_dossier,
            name="generate_dossier",
            title="Generate offboarding dossier content",
            description=(
                "Generate the summary and sections of an offboarding handover dossier from a "
                "completed interview transcript. Backed by an LLM that may consult prior "
                "dossiers and the SOP index for extra context. Returns typed dossier sections "
                "ready to persist."
            ),
        )

    @tool_error_handler
    async def generate_dossier(self, interview_transcript: str) -> GenerateDossierResponse:
        """Generate dossier content from an interview transcript.

        Args:
            interview_transcript (str): Plain-text Q/A transcript of the completed interview.
        Returns:
            GenerateDossierResponse with the generated summary and sections.
        """
        if not interview_transcript.strip():
            raise ToolError("'interview_transcript' must not be empty.")
        return await self.__service.generate(interview_transcript)
