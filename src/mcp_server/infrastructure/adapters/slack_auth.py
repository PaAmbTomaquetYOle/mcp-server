from urllib.parse import urlencode

from httpx2 import AsyncClient, HTTPStatusError

from mcp_server.application.ports import ISlackAuthPort, ITokenStoragePort
from mcp_server.application.ports.slack_auth import SlackAuthResult
from mcp_server.domain import AuthCodeExchangeException

SLACK_AUTH_URL = "https://slack.com/oauth/v2/authorize"
SLACK_TOKEN_URL = "https://slack.com/api/oauth.v2.access"
SLACK_USER_SEARCH_SCOPES = (
    "search:read.public,search:read.private,search:read.im,"
    "search:read.mpim,search:read.files,search:read.users"
)


class SlackAuthAdapter(ISlackAuthPort):
    """Handles Slack OAuth 2.0 user-token authentication for the workspace search connector."""

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
            "client_id": self.__client_id,
            "user_scope": SLACK_USER_SEARCH_SCOPES,
            "redirect_uri": self.__redirect_uri,
            "state": state,
        }
        return f"{SLACK_AUTH_URL}?{urlencode(params)}"

    async def exchange_auth_code(self, code: str) -> SlackAuthResult:
        try:
            async with AsyncClient() as client:
                response = await client.post(
                    SLACK_TOKEN_URL,
                    data={
                        "client_id": self.__client_id,
                        "client_secret": self.__client_secret,
                        "code": code,
                        "redirect_uri": self.__redirect_uri,
                    },
                )
                response.raise_for_status()
                data = response.json()

                if not data.get("ok", False):
                    raise AuthCodeExchangeException("unknown", str(data.get("error")))

                authed_user = data["authed_user"]
                slack_user_id = authed_user["id"]
                access_token = authed_user["access_token"]
                team_id = data["team"]["id"]

        except AuthCodeExchangeException:
            raise
        except HTTPStatusError as exc:
            raise AuthCodeExchangeException(
                "unknown", f"HTTP {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except Exception as exc:
            raise AuthCodeExchangeException("unknown", str(exc)) from exc

        await self.__token_storage.save_tokens(slack_user_id, access_token, "", 0)

        return SlackAuthResult(slack_user_id=slack_user_id, team_id=team_id, access_token=access_token)
