from abc import ABC, abstractmethod
from collections.abc import Iterable

from mcp_server.domain import CollaborationTask


class ICollaborationToolIntegrationService(ABC):
    """Interface for the Collaboration Tool Integration Service."""

    @abstractmethod
    async def get_issue(self, issue_id: str, user_id: str) -> CollaborationTask:
        pass #TODO: Update method return value

    @abstractmethod
    async def get_pending_issues(self, user_id: str, assignee: str) -> Iterable[CollaborationTask]:
        pass #TODO: Update method return value