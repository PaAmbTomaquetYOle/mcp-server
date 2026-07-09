from abc import ABC, abstractmethod
from typing import TypedDict


class TokenData(TypedDict):
    """
    TypedDict representing the structure of OAuth token data for a user.
    """
    access_token: str
    refresh_token: str
    expires_at: int


class AuthResult(TypedDict):
    """Result of a successful OAuth token exchange, including the resolved user email."""
    email: str
    access_token: str
    refresh_token: str
    expires_at: int


class ITokenStoragePort(ABC):
    """Interface for storing and retrieving OAuth tokens per user."""

    @abstractmethod
    async def get_tokens(self, user_id: str) -> TokenData | None:
        """Return tokens for user, or None if not found.

        Args:
            user_id: The ID of the user these tokens belong to.
        Returns:
            A TokenData dict containing access_token, refresh_token, and expires_at,
            or None if no tokens are found for the user.
        """

    @abstractmethod
    async def save_tokens(
        self,
        user_id: str,
        access_token: str,
        refresh_token: str,
        expires_at: int,
    ) -> None:
        """
        Store or update tokens for a user.

        Args:
            user_id: The ID of the user these tokens belong to.
            access_token: The OAuth access token.
            refresh_token: The OAuth refresh token.
            expires_at: Unix timestamp when the access token expires.
        """

    @abstractmethod
    async def delete_tokens(self, user_id: str) -> None:
        """
        Remove tokens for a user.

        Args:
            user_id: The ID of the user whose tokens should be deleted.
        """
