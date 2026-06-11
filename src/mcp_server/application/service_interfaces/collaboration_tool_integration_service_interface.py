from abc import ABC, abstractmethod
from collections.abc import Iterable

from mcp_server.domain import CollaborationTask


class ICollaborationToolIntegrationService(ABC):
    """Interface for the Collaboration Tool Integration Service."""

    @abstractmethod
    async def get_issue(self, issue_id: str, user_id: str) -> CollaborationTask:
        """
        Retrieve a specific issue/task from the collaboration tool by its ID.

        Args:
            issue_id (str): The ID of the issue/task to retrieve.
            user_id (str): The ID of the user making the request, used for authentication.
        Returns:
            A domain model representing the issue/task.
        """

    @abstractmethod
    async def get_pending_issues(self, user_id: str, assignee: str) -> Iterable[CollaborationTask]:
        """
        Retrieve all pending issues/tasks from the collaboration tool, filtered by assignee.

        Args:
            user_id (str): The ID of the user making the request, used for authentication.
            assignee (str): The username of the assignee to filter issues by.
        Returns:
            An iterable of domain models representing the pending issues/tasks.
        """