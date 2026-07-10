class DomainException(Exception):
    """Base exception for all MCP server domain errors."""


class UserTokensNotFoundException(DomainException):
    """No OAuth tokens found for the given user."""

    def __init__(self, user_id: str) -> None:
        super().__init__(f"No tokens found for user: {user_id}")
        self.user_id = user_id


class TokenRefreshException(DomainException):
    """Failed to refresh the OAuth access token."""

    def __init__(self, user_id: str, reason: str) -> None:
        super().__init__(f"Token refresh failed for user {user_id}: {reason}")
        self.user_id = user_id
        self.reason = reason


class JiraApiException(DomainException):
    """Jira REST API returned an error."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class IssueNotFoundException(JiraApiException):
    """The requested Jira issue does not exist."""

    def __init__(self, issue_id: str) -> None:
        super().__init__(f"Issue not found: {issue_id}", status_code=404)
        self.issue_id = issue_id


class JiraUserNotFoundException(JiraApiException):
    """The specified assignee was not found in Jira."""

    def __init__(self, assignee: str) -> None:
        super().__init__(f"Jira user not found: {assignee}", status_code=404)
        self.assignee = assignee


class JiraAuthenticationException(DomainException):
    """Authentication with Jira failed (invalid or revoked credentials)."""

    def __init__(self, user_id: str) -> None:
        super().__init__(
            f"Jira authentication failed for user {user_id}. "
            "Token may be invalid or revoked — re-authentication required."
        )
        self.user_id = user_id


class TrelloApiException(DomainException):
    """Trello REST API returned an error."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class TrelloCardNotFoundException(TrelloApiException):
    """The requested Trello card does not exist."""

    def __init__(self, card_id: str) -> None:
        super().__init__(f"Trello card not found: {card_id}", status_code=404)
        self.card_id = card_id


class TrelloMemberNotFoundException(TrelloApiException):
    """The specified member was not found in Trello."""

    def __init__(self, member: str) -> None:
        super().__init__(f"Trello member not found: {member}", status_code=404)
        self.member = member


class TrelloAuthenticationException(DomainException):
    """Authentication with Trello failed (invalid or revoked credentials)."""

    def __init__(self, user_id: str) -> None:
        super().__init__(
            f"Trello authentication failed for user {user_id}. "
            "Token may be invalid or revoked — re-authentication required."
        )
        self.user_id = user_id


class TrelloTokenStorageException(DomainException):
    """Failed to store Trello OAuth tokens (e.g. empty token or token_secret)."""

    def __init__(self, user_id: str, reason: str) -> None:
        super().__init__(f"Trello token storage failed for user {user_id}: {reason}")
        self.user_id = user_id
        self.reason = reason


class BackendApiException(DomainException):
    """The backend API returned an error or is unreachable."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class KnowledgeGraphException(DomainException):
    """Base exception for all Knowledge Graph errors."""


class PersonNotFoundException(KnowledgeGraphException):
    """The requested person was not found in the knowledge graph."""

    def __init__(self, person_id: str) -> None:
        super().__init__(f"Person not found: {person_id}")
        self.person_id = person_id
        self.status_code = 404


class KnowledgeGraphApiException(KnowledgeGraphException):
    """The Knowledge Graph REST API returned an error or is unreachable."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class EventPublishException(KnowledgeGraphException):
    """Failed to publish an event to the message broker."""

    def __init__(self, reason: str) -> None:
        super().__init__(f"Event publish failed: {reason}")
        self.reason = reason


class AuthCodeExchangeException(DomainException):
    """Failed to exchange an OAuth authorization code for tokens."""

    def __init__(self, user_id: str, reason: str) -> None:
        super().__init__(
            f"Auth code exchange failed for user {user_id}: {reason}"
        )
        self.user_id = user_id
        self.reason = reason


class SlackSearchException(DomainException):
    """Base exception for the Slack search connector."""


class SlackApiException(SlackSearchException):
    """The Slack API returned an error or is unreachable."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class SopCacheException(SlackSearchException):
    """Failed to refresh the in-memory SOP search cache."""

    def __init__(self, reason: str) -> None:
        super().__init__(f"SOP cache refresh failed: {reason}")
        self.reason = reason


class SearchTimeoutException(SlackSearchException):
    """A search took longer than the Slack function-execution deadline."""

    def __init__(self, query: str) -> None:
        super().__init__(f"Search timed out for query: {query}")
        self.query = query
