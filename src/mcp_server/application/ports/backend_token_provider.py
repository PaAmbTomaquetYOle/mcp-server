from abc import ABC, abstractmethod


class IBackendTokenProvider(ABC):
    """
    Interface for obtaining access tokens for the backend API.

    Implementations authenticate against the backend's client-credentials
    token endpoint and are responsible for caching/refreshing the token.
    """

    @abstractmethod
    async def get_access_token(self) -> str:
        """
        Return a valid access token for the backend API, refreshing it first if needed.
        """
