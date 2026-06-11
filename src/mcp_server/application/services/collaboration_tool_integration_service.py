from mcp_server.application import ICollaborationToolIntegrationService, ICollaborationToolPort


class CollaborationToolIntegrationService(ICollaborationToolIntegrationService):
    """
    Service that integrates with external collaboration tools (e.g., Jira, Trello).
    """
    __collaboration_tool_port: ICollaborationToolPort

    async def get_issue(self, issue_id: str):
        return await self.__collaboration_tool_port.get_issue(issue_id)