from collections.abc import Iterable

from mcp_server.application import ICollaborationToolIntegrationService, ICollaborationToolPort
from mcp_server.domain import CollaborationTask


class CollaborationToolIntegrationService(ICollaborationToolIntegrationService):
    """
    Service that integrates with external collaboration tools (e.g., Jira, Trello).
    """
    __collaboration_tool_port: ICollaborationToolPort

    def __init__(self, collaboration_tool_port: ICollaborationToolPort):
        self.__collaboration_tool_port = collaboration_tool_port

    async def get_issue(self, issue_id: str, user_id: str) -> CollaborationTask:
        """
        Retrieve a specific issue/task from the collaboration tool by its ID.
        """
        return await self.__collaboration_tool_port.get_issue(issue_id, user_id)
    
    async def get_pending_issues(self, user_id: str, assignee: str) -> Iterable[CollaborationTask]:
        """
        Retrieve all pending issues/tasks from the collaboration tool, filtered by assignee.
        """
        return await self.__collaboration_tool_port.get_pending_issues(user_id, assignee)