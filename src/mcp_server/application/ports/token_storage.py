from abc import ABC, abstractmethod


class ITokenStoragePort(ABC):
    """Interface for storing and retrieving OAuth tokens per user."""

    @abstractmethod
    async def get_tokens(self, user_id: str) -> dict | None:
        """Return tokens for user, or None if not found.

        Expected dict keys: access_token, refresh_token, expires_at.
        """

    @abstractmethod
    async def save_tokens(
        self,
        user_id: str,
        access_token: str,
        refresh_token: str,
        expires_at: int,
    ) -> None:
        """Store or update tokens for a user."""

    @abstractmethod
    async def delete_tokens(self, user_id: str) -> None:
        """Remove tokens for a user."""
