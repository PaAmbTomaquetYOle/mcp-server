from abc import ABC, abstractmethod
from typing import Any


class ISlackApiPort(ABC):
    """Interface for calling the Slack Web API from the search connector."""

    @abstractmethod
    async def complete_search_success(self, function_execution_id: str, results: list[dict[str, Any]]) -> None:
        """
        Report a successful search function execution back to Slack, with results.

        Args:
            function_execution_id: The ID of the function execution being completed.
            results: List of search result objects (external_ref, title, description, link, date_updated, content).
        """

    @abstractmethod
    async def complete_search_error(self, function_execution_id: str, error: str) -> None:
        """
        Report a failed search function execution back to Slack.

        Args:
            function_execution_id: The ID of the function execution being completed.
            error: A user-friendly error message to display to the searching user.
        """

    @abstractmethod
    async def update_user_connection(self, user_id: str, status: str) -> None:
        """
        Update the connection status between a Slack user and this app.

        Args:
            user_id: The Slack user ID.
            status: Either "connected" or "disconnected".
        """

    @abstractmethod
    async def present_entity_details(self, trigger_id: str, metadata: dict[str, Any]) -> None:
        """
        Deliver Work Object metadata to the search-result flexpane.

        Args:
            trigger_id: The trigger ID from the entity_details_requested event.
            metadata: The Work Object metadata payload describing the entity.
        """
