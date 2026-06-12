import asyncio
from collections.abc import Iterable

from trello import Card, Member, TrelloClient

from mcp_server.application.ports import ICollaborationToolPort, ITokenStoragePort, TokenData
from mcp_server.domain import TrelloMember, TrelloTask
from mcp_server.domain.exceptions import UserTokensNotFoundException


class TrelloAdapter(ICollaborationToolPort):
    __token_storage: ITokenStoragePort
    __api_key: str
    __api_secret: str

    def __init__(
        self,
        token_storage_port: ITokenStoragePort,
        api_key: str,
        api_secret: str,
    ) -> None:
        """
        Initializes the TrelloAdapter with necessary configuration and token storage.

        Args:
            token_storage_port (ITokenStoragePort): Port for storing and retrieving OAuth tokens.
            api_key (str): API key for Trello integration.
            api_secret (str): API secret for Trello integration.
        """
        self.__token_storage = token_storage_port
        self.__api_key = api_key
        self.__api_secret = api_secret

    async def _get_tokens(self, user_id: str) -> TokenData:
        """
        Retrieve OAuth tokens for a user from storage. Raises UserTokensNotFoundException if not found.

        Args:
            user_id (str): The ID of the user whose tokens to retrieve.
        Returns:
            TokenData: A dict containing access_token, refresh_token, and expires_at.
        Raises:
            UserTokensNotFoundException: If no tokens are found for the user.
        """
        tokens: TokenData | None = await self.__token_storage.get_tokens(user_id)
        if tokens is None:
            raise UserTokensNotFoundException(user_id)
        if not tokens["access_token"] or not tokens["refresh_token"]:
            raise UserTokensNotFoundException(user_id)
        return tokens

    def _build_client(self, token: str, token_secret: str) -> TrelloClient:
        """
        Build and return a TrelloClient instance authenticated with the provided token and token secret.

        Args:
            token (str): The OAuth access token for Trello.
            token_secret (str): The OAuth token secret for Trello.
        Returns:
            TrelloClient: An instance of TrelloClient authenticated with the provided credentials.
        """
        # Trello's "basic OAuth" is OAuth 1.0a: token and token_secret are the
        # credential pair the client needs to sign requests.
        return TrelloClient(
            api_key=self.__api_key,
            api_secret=self.__api_secret,
            token=token,
            token_secret=token_secret,
        )

    async def _get_client(self, user_id: str) -> TrelloClient:
        """
        Build a TrelloClient for the given user ID, retrieving tokens from storage.

        Args:
            user_id (str): The ID of the user whose tokens to retrieve.
        Returns:
            TrelloClient: An instance of TrelloClient authenticated with the user's tokens.
        Raises:
            UserTokensNotFoundException: If no tokens are found for the user.
        """
        tokens = await self._get_tokens(user_id)
        return self._build_client(tokens["access_token"], tokens["refresh_token"])

    @staticmethod
    def __member_to_domain_model(member: Member) -> TrelloMember:
        """
        Convert a TrelloMember model into a domain model.

        Args:
            member (Member): The TrelloMember model to convert.
        Returns:
            TrelloMember: A domain model representing the Trello member.
        """
        return TrelloMember(
            id=member.id,
            username=member.username,
            email=member.email
        )

    async def __card_to_domain_model(self, card: Card, user_id: str) -> TrelloTask:
        """
        Convert a Trello Card object to a TrelloTask domain model.

        Args:
            card (Card): The Trello Card object to convert.
            user_id (str): The ID of the user whose tasks to retrieve.
        Returns:
            TrelloTask: A domain model representing the Trello task.
        """
        client = await self._get_client(user_id)

        return TrelloTask(
            task_id=card.id,
            title=card.name,
            description=card.description,
            url=card.url,
            due_date=card.due,
            list_id=card.list_id,
            board_id=card.board_id,
            labels=[label.name for label in card.labels],
            members=[
                self.__member_to_domain_model(member) for member in [
                    await asyncio.to_thread(client.get_member, member_id) for member_id in card.idMembers
                ]
            ]
        )

    async def get_issue(self, issue_id: str, user_id: str) -> TrelloTask:
        client = await self._get_client(user_id)
        card: Card = await asyncio.to_thread(client.get_card, issue_id)
        return await self.__card_to_domain_model(card, user_id)

    async def get_pending_issues(self, user_id: str, assignee: str) -> Iterable[TrelloTask]:
        raise NotImplementedError("Trello pending issue retrieval is not implemented yet.")
