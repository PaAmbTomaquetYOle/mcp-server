from pydantic import BaseModel, Field

from mcp_server.domain import CollaborationToolEnum
from mcp_server.domain.collaboration_tasks import CollaborationTask


class JiraUser(BaseModel):
    """Represents a Jira user."""
    display_name: str = Field(
        title="Display name",
        description="Display name of the user",
    )
    email: str = Field(
        title="Email address",
        description="Email address of the user",
    )
    name: str = Field(
        title="Name",
        description="Name of the user",
    )

class JiraTask(CollaborationTask):
    """Represents a Jira task related to collaboration tool integration."""
    collaboration_tool: CollaborationToolEnum = Field(description="Name of the collaboration tool", examples=["JIRA"], default=CollaborationToolEnum.JIRA)
    priority: str | None = Field(
        description="Priority level of the Jira issue", examples=["low", "medium", "high"]
    )
    issue_key: str = Field(
        description="Jira issue key", examples=["PROJ-123"]
    )
    reporter: JiraUser = Field(
        description="Reporter of the Jira issue",
    )
    assignee: JiraUser | None = Field(
        description="Assignee of the Jira issue",
    )
    creator: JiraUser = Field(
        description="Creator of the Jira issue",
    )
    issue_type: str = Field(
        description="Type of the Jira issue",
    )
