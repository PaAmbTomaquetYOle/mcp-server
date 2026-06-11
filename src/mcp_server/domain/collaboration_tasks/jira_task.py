from pydantic import Field

from mcp_server.domain.collaboration_tasks import CollaborationTask
from mcp_server.domain import CollaborationToolEnum


class JiraTask(CollaborationTask):
    """Represents a Jira task related to collaboration tool integration."""
    collaboration_tool: CollaborationToolEnum = Field(description="Name of the collaboration tool", examples=["JIRA"], default=CollaborationToolEnum.JIRA)