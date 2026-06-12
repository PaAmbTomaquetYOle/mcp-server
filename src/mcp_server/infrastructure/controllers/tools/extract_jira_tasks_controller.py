from typing import cast

from mcp.server import FastMCP

from mcp_server.application.service_interfaces import ICollaborationToolIntegrationService
from mcp_server.domain import JiraTask
from mcp_server.infrastructure.controllers.base_controller import BaseController
from mcp_server.infrastructure.controllers.error_handler import tool_error_handler


class ExtractJiraTasksToolController(BaseController):
    """Controller for the tool that extracts Jira tasks related to collaboration tool integration."""
    __jira_service: ICollaborationToolIntegrationService

    def __init__(self, server: FastMCP, jira_service: ICollaborationToolIntegrationService) -> None:
        super().__init__(server)
        self.__jira_service = jira_service

    def register(self) -> None:
        self._server.add_tool(
            self.get_jira_issue,
            name="get_jira_issue",
            description="Get a specific Jira issue by its ID. Requires authentication via user_id.",
        )
        self._server.add_tool(
            self.get_pending_jira_issues,
            name="get_pending_jira_issues",
            description="Get all pending Jira issues assigned to a specific user. Requires authentication via user_id and filtering by assignee.",
        )

    @tool_error_handler
    async def get_jira_issue(self, issue_id: str, user_id: str) -> JiraTask:
        """
        Get a specific Jira issue by its ID.

        Args:
            issue_id (str): The ID of the Jira issue to retrieve.
            user_id (str): The ID of the user making the request, used for authentication.
        Returns:
            A domain model representing the Jira issue.
        """
        jira_task = await self.__jira_service.get_issue(issue_id, user_id)
        return cast(JiraTask, jira_task)

    @tool_error_handler
    async def get_pending_jira_issues(self, user_id: str, assignee: str) -> tuple[JiraTask, ...]:
        """
        Get all pending Jira issues assigned to a specific user.

        Args:
            user_id (str): The ID of the user making the request, used for authentication.
            assignee (str): The username of the assignee to filter issues by.
        Returns:
            A tuple of domain models representing the pending Jira issues.
        """
        jira_tasks = await self.__jira_service.get_pending_issues(user_id, assignee)
        return tuple(cast(JiraTask, task) for task in jira_tasks)
