from abc import ABC, abstractmethod
from collections.abc import Iterable

from mcp_server.domain import CollaborationTask


class ICollaborationToolPort(ABC):
    """Interface for the Collaboration Tool Port."""

    @abstractmethod
    async def get_issue(self, issue_id: str, user_id: str) -> CollaborationTask:
        """
        Retrieve a specific issue/task from the collaboration tool by its ID.
        """

    @abstractmethod
    async def get_pending_issues(self, user_id: str, assignee: str) -> Iterable[CollaborationTask]:
        """
        Retrieve all pending issues/tasks from the collaboration tool, filtered by assignee.
        """