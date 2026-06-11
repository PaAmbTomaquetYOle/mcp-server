from abc import ABC, abstractmethod


class ICollaborationToolIntegrationService(ABC):
    """Interface for the Collaboration Tool Integration Service."""

    @abstractmethod
    async def get_issue(issue_id: str):
        pass #TODO: Update method return value