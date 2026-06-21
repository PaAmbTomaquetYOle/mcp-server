from abc import ABC, abstractmethod


class ITrelloAuthService(ABC):
    """Interface for the Trello authentication use case."""

    @abstractmethod
    async def generate_auth_url(self, user_id: str) -> str:
        """Generate the Trello OAuth authorization URL.

        Args:
            user_id: Identifier for the user initiating the authorization.
        Returns:
            The authorization URL the user must visit to grant consent.
        """

    @abstractmethod
    async def store_tokens(self, user_id: str, token: str, token_secret: str) -> None:
        """Persist Trello OAuth token credentials.

        Args:
            user_id: Identifier for the user these tokens belong to.
            token: The OAuth access token from Trello.
            token_secret: The OAuth token secret from Trello.
        """
