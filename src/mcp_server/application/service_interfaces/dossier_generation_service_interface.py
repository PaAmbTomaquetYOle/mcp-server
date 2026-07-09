from abc import ABC, abstractmethod

from mcp_server.infrastructure.dto.tools.dossier_schemas import GenerateDossierResponse


class IDossierGenerationService(ABC):
    """Interface for the offboarding dossier content generation use case."""

    @abstractmethod
    async def generate(self, interview_transcript: str) -> GenerateDossierResponse:
        """Generate the summary and sections of a dossier from an interview transcript.

        Args:
            interview_transcript: Plain-text Q/A transcript of the completed
                offboarding interview.
        Returns:
            The generated summary and typed dossier sections.
        """
