from typing import Iterable

from mcp_server.application import ICollaborationToolPort
from mcp_server.domain import TrelloTask


class TrelloAdapter(ICollaborationToolPort):

    async def get_issue(self, issue_id: str, user_id: str) -> TrelloTask:
        pass
    
    async def get_pending_issues(self, user_id: str, assignee: str) -> Iterable[TrelloTask]:
        pass
    