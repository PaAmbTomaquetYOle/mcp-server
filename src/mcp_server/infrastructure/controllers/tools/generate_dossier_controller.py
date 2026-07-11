from mcp.server import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from mcp_server.application.service_interfaces.dossier_generation_service_interface import (
    IDossierGenerationService,
    ReviewScope,
)
from mcp_server.infrastructure.controllers.base_controller import BaseController
from mcp_server.infrastructure.controllers.error_handler import tool_error_handler
from mcp_server.infrastructure.dto import GenerateDossierResponse


class GenerateDossierToolController(BaseController):
    """Controller for the tool that generates dossier content via an LLM.

    Covers offboarding handover dossiers as well as monthly/annual
    knowledge-retention review dossiers (MCP-15).
    """

    __service: IDossierGenerationService

    def __init__(self, server: FastMCP, service: IDossierGenerationService) -> None:
        super().__init__(server)
        self.__service = service

    def register(self) -> None:
        self._server.add_tool(
            self.generate_dossier,
            name="generate_dossier",
            title="Generate dossier content",
            description=(
                "Generate the summary and sections of a handover dossier from a completed "
                "interview transcript. 'review_scope' selects the dossier style: "
                "'offboarding' (default) for a departing employee's handover, 'monthly' for a "
                "lightweight recurring knowledge-retention check-in (recent activity only), or "
                "'annual' for an exhaustive yearly knowledge-retention review (all accumulated "
                "knowledge). Backed by an LLM that may consult prior dossiers and the SOP index "
                "for extra context. Returns typed dossier sections ready to persist."
            ),
        )

    @tool_error_handler
    async def generate_dossier(
        self, interview_transcript: str, review_scope: ReviewScope = "offboarding"
    ) -> GenerateDossierResponse:
        """Generate dossier content from an interview transcript.

        Args:
            interview_transcript (str): Plain-text Q/A transcript of the completed interview.
            review_scope (ReviewScope): Which kind of dossier to write. Defaults to
                "offboarding".
        Returns:
            GenerateDossierResponse with the generated summary and sections.
        """
        if not interview_transcript.strip():
            raise ToolError("'interview_transcript' must not be empty.")
        return await self.__service.generate(interview_transcript, review_scope)
