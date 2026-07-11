from abc import ABC, abstractmethod
from typing import Literal

from mcp_server.infrastructure.dto.tools.dossier_schemas import GenerateDossierResponse

ReviewScope = Literal["offboarding", "monthly", "annual"]


class IDossierGenerationService(ABC):
    """Interface for the dossier content generation use case.

    Covers offboarding dossiers as well as monthly/annual knowledge-retention
    review dossiers (MCP-15) — the ``review_scope`` selects the prompt and
    token budget used.
    """

    @abstractmethod
    async def generate(
        self, interview_transcript: str, review_scope: ReviewScope = "offboarding"
    ) -> GenerateDossierResponse:
        """Generate the summary and sections of a dossier from an interview transcript.

        Args:
            interview_transcript: Plain-text Q/A transcript of the completed
                interview.
            review_scope: Which kind of dossier to write — "offboarding" (the
                default, unchanged from before MCP-15), "monthly" (lightweight,
                recent activity only), or "annual" (exhaustive, all
                accumulated knowledge).
        Returns:
            The generated summary and typed dossier sections.
        """
