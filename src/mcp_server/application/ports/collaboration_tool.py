from abc import ABC, abstractmethod


class ICollaborationToolPort(ABC):
    """Interface for the Collaboration Tool Port."""

    @abstractmethod
    async def get_issue(issue_id: str):
        pass #TODO: Update method return value