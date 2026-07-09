from mcp.server.fastmcp.prompts.base import Prompt

from mcp_server.infrastructure.controllers import BaseController


class TrelloLoginPromptController(BaseController):
    """Prompt controller that guides an agent through the Trello OAuth 1.0a login flow."""

    def register(self) -> None:
        self._server.add_prompt(
            Prompt(
                name="trello_login",
                title="Trello Login",
                description="Guide the user through the Trello OAuth 1.0a authorization flow.",
                fn=self.trello_login,
                arguments=[],
                context_kwarg=None,
            )
        )

    @staticmethod
    async def trello_login() -> str:
        return (
            "You are a Trello authentication assistant. Your goal is to help the user "
            "connect their Trello account via OAuth 1.0a.\n\n"
            "Follow these steps:\n\n"
            "1. Call the `generate_trello_auth_url` tool (no arguments needed).\n"
            "2. Present the returned authorization URL to the user and ask them to open it in their browser.\n"
            "3. Tell the user they will be redirected to Trello to log in and grant permissions.\n"
            "4. After authorizing, the user will receive an OAuth token. "
            "Ask the user to provide this token.\n"
            "5. Call `complete_trello_auth` with the token. "
            "The tool will automatically resolve the Trello username and store the credentials.\n"
            "6. The returned user_id (Trello username) must be used consistently in all subsequent "
            "Trello tool calls (e.g. `get_pending_trello_cards`, `get_trello_issue`).\n\n"
            "Important: the user does NOT need to provide a user_id — it is resolved automatically "
            "from the OAuth token via the Trello API."
        )
