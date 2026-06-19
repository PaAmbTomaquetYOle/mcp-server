import time
from typing import Any
from urllib.parse import urlencode

from httpx2 import AsyncClient, HTTPStatusError

from mcp_server.application.ports import IJiraAuthPort, ITokenStoragePort, TokenData
from mcp_server.domain import AuthCodeExchangeException

ATLASSIAN_AUTH_URL = "https://auth.atlassian.com/authorize"
ATLASSIAN_TOKEN_URL = "https://auth.atlassian.com/oauth/token"
JIRA_OAUTH_SCOPES = "read:jira-work read:jira-user offline_access"


class JiraAuthAdapter(IJiraAuthPort):

    __token_storage: ITokenStoragePort
    __client_id: str
    __client_secret: str
    __redirect_uri: str

    def __init__(
        self,
        token_storage_port: ITokenStoragePort,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ) -> None:
        self.__token_storage = token_storage_port
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__redirect_uri = redirect_uri

    async def generate_auth_url(self, user_id: str) -> str:
        params = {
            "audience": "api.atlassian.com",
            "client_id": self.__client_id,
            "scope": JIRA_OAUTH_SCOPES,
            "redirect_uri": self.__redirect_uri,
            "state": user_id,
            "response_type": "code",
            "prompt": "consent",
        }
        return f"{ATLASSIAN_AUTH_URL}?{urlencode(params)}"

    async def exchange_auth_code(self, user_id: str, code: str) -> TokenData:
        try:
            async with AsyncClient() as client:
                response = await client.post(
                    ATLASSIAN_TOKEN_URL,
                    json={
                        "grant_type": "authorization_code",
                        "client_id": self.__client_id,
                        "client_secret": self.__client_secret,
                        "code": code,
                        "redirect_uri": self.__redirect_uri,
                    },
                )
                response.raise_for_status()
                data: dict[str, Any] = response.json()
        except HTTPStatusError as exc:
            raise AuthCodeExchangeException(
                user_id, f"HTTP {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except Exception as exc:
            raise AuthCodeExchangeException(user_id, str(exc)) from exc

        tokens: TokenData = {
            "access_token": str(data["access_token"]),
            "refresh_token": str(data["refresh_token"]),
            "expires_at": int(time.time()) + int(data["expires_in"]),
        }
        await self.__token_storage.save_tokens(
            user_id,
            tokens["access_token"],
            tokens["refresh_token"],
            tokens["expires_at"],
        )
        return tokens
