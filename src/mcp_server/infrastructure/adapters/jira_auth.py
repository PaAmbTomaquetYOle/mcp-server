import time
from typing import Any
from urllib.parse import urlencode

from httpx2 import AsyncClient, HTTPStatusError

from mcp_server.application.ports import IJiraAuthPort, ITokenStoragePort
from mcp_server.application.ports.token_storage import AuthResult
from mcp_server.domain import AuthCodeExchangeException

ATLASSIAN_AUTH_URL = "https://auth.atlassian.com/authorize"
ATLASSIAN_TOKEN_URL = "https://auth.atlassian.com/oauth/token"
ATLASSIAN_ME_URL = "https://api.atlassian.com/me"
JIRA_OAUTH_SCOPES = "read:me read:jira-work read:jira-user offline_access"


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

    async def generate_auth_url(self, state: str) -> str:
        params = {
            "audience": "api.atlassian.com",
            "client_id": self.__client_id,
            "scope": JIRA_OAUTH_SCOPES,
            "redirect_uri": self.__redirect_uri,
            "state": state,
            "response_type": "code",
            "prompt": "consent",
        }
        return f"{ATLASSIAN_AUTH_URL}?{urlencode(params)}"

    async def exchange_auth_code(self, code: str) -> AuthResult:
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

                access_token = str(data["access_token"])
                refresh_token = str(data["refresh_token"])
                expires_at = int(time.time()) + int(data["expires_in"])

                email = await self._fetch_user_email(client, access_token)

        except AuthCodeExchangeException:
            raise
        except HTTPStatusError as exc:
            raise AuthCodeExchangeException(
                "unknown", f"HTTP {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except Exception as exc:
            raise AuthCodeExchangeException("unknown", str(exc)) from exc

        await self.__token_storage.save_tokens(email, access_token, refresh_token, expires_at)

        return AuthResult(
            email=email,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
        )

    async def _fetch_user_email(self, client: AsyncClient, access_token: str) -> str:
        try:
            response = await client.get(
                ATLASSIAN_ME_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return str(response.json()["email"])
        except Exception as exc:
            raise AuthCodeExchangeException(
                "unknown", f"Failed to fetch user email from Atlassian: {exc}"
            ) from exc
