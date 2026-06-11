class CollaborationToolException(Exception):
    """Base exception for all collaboration tool errors."""


class UserTokensNotFoundException(CollaborationToolException):
    """No OAuth tokens found for the given user."""

    def __init__(self, user_id: str) -> None:
        super().__init__(f"No tokens found for user: {user_id}")
        self.user_id = user_id


class TokenRefreshException(CollaborationToolException):
    """Failed to refresh the OAuth access token."""

    def __init__(self, user_id: str, reason: str) -> None:
        super().__init__(f"Token refresh failed for user {user_id}: {reason}")
        self.user_id = user_id
        self.reason = reason


class JiraApiException(CollaborationToolException):
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


class JiraAuthenticationException(CollaborationToolException):
    """Authentication with Jira failed (invalid or revoked credentials)."""

    def __init__(self, user_id: str) -> None:
        super().__init__(
            f"Jira authentication failed for user {user_id}. "
            "Token may be invalid or revoked — re-authentication required."
        )
        self.user_id = user_id
