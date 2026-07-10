from pydantic import BaseModel, Field

from mcp_server.domain import CollaborationToolEnum
from mcp_server.domain.collaboration_tasks import CollaborationTask


class TrelloMember(BaseModel):
    """Represents a Trello member model."""
    id: str = Field(
        description="ID of the Trello member that belongs to the Trello board"
    )
    username: str = Field(
        description="Username of the Trello member that belongs to the Trello board"
    )
    email: str = Field(
        description="Email of the Trello member that belongs to the Trello board"
    )

class TrelloTask(CollaborationTask):
    """Represents a Trello task related to collaboration tool integration."""
    collaboration_tool: CollaborationToolEnum = Field(
        description="Name of the collaboration tool",
        examples=["TRELLO"],
        default=CollaborationToolEnum.TRELLO
    )
    due_date: str | None = Field(
        description="Due date of the Trello task in ISO 8601 format",
        examples=["2024-12-31T23:59:59Z"]
    )
    list_id: str = Field(
        description="ID of the Trello list that the task belongs to"
    )
    board_id: str = Field(
        description="ID of the Trello board that the task belongs to"
    )
    labels: list[str] = Field(
        description="Labels of the Trello board that the task belongs to"
    )
    members: list[TrelloMember] = Field(
        description="Members of the Trello board that the task belongs to"
    )