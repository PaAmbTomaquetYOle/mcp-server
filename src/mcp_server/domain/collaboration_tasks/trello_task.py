from pydantic import Field

from mcp_server.domain.collaboration_tasks import CollaborationTask
from mcp_server.domain import CollaborationToolEnum

class TrelloTask(CollaborationTask):
    """Represents a Trello task related to collaboration tool integration."""
    collaboration_tool: CollaborationToolEnum = Field(description="Name of the collaboration tool", examples=["TRELLO"], default=CollaborationToolEnum.TRELLO)