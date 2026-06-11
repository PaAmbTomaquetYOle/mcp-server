from abc import ABC

from pydantic import BaseModel, Field

from mcp_server.domain import CollaborationToolEnum

class CollaborationTask(BaseModel, ABC):
    """Represents a task related to collaboration tool integration."""

    task_id: str = Field(description="Unique identifier for the collaboration task")
    description: str = Field(description="Detailed description of the collaboration task")
    title: str = Field(description="Title of the collaboration task")
    status: str = Field(description="Current status of the collaboration task", examples=["pending", "in_progress", "completed"])
    priority: str | None = Field(description="Priority level of the collaboration task", examples=["low", "medium", "high"])
    project: str = Field(description="Project associated with the collaboration task")
    url: str = Field(description="URL to the collaboration task in the external tool")
    collaboration_tool: CollaborationToolEnum = Field(description="Name of the collaboration tool", examples=["JIRA", "TRELLO"])