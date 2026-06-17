from __future__ import annotations

from typing import cast

from mcp.server import FastMCP

from mcp_server.application import ICollaborationToolIntegrationService
from mcp_server.domain import TrelloTask
from mcp_server.infrastructure.controllers import BaseController, tool_error_handler


class ExtractTrelloTasksToolController(BaseController):
    """Controller for the trello tasks tool."""

    __trello_service: ICollaborationToolIntegrationService

    def __init__(self, server: FastMCP, trello_service: ICollaborationToolIntegrationService) -> None:
        super().__init__(server)
        self.__trello_service = trello_service

    def register(self) -> None:
        self._server.add_tool(
            self.get_trello_card,
            name="get_trello_card",
            title="Extract a specific Trello card",
            description="Get a specific Trello card by its ID. Requires authentication via user_id.",
        )
        self._server.add_tool(
            self.get_pending_trello_cards,
            name="get_pending_trello_cards",
            title="Extract all pending Trello cards",
            description=("Get all pending Trello cards assigned to a specific user."
                         "Requires authentication via user_id and filtering by assignee."),
        )

    @tool_error_handler
    async def get_trello_card(self, card_id: str, user_id: str) -> TrelloTask:
        """
        Get a specific Trello card by its ID.

        Args:
            card_id (str): The ID of the Trello card to retrieve.
            user_id (str): The ID of the user making the request, used for authentication.
        Returns:
            A domain model representing the Trello card.
        """
        trello_card = await self.__trello_service.get_issue(card_id, user_id)
        return cast(TrelloTask, trello_card)
    
    @tool_error_handler
    async def get_pending_trello_cards(self, user_id: str, assignee: str) -> tuple[TrelloTask, ...]:
        """
        Get all pending Trello cards assigned to a specific user.

        Args:
            user_id (str): The ID of the user making the request, used for authentication.
            assignee (str): The username of the assignee to filter issues by.
        Returns:
            A tuple of domain models representing the pending Trello cards.
        """
        trello_cards = await self.__trello_service.get_pending_issues(user_id, assignee)
        return tuple(cast(TrelloTask, t) for t in trello_cards)