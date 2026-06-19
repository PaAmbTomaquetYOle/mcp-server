from pydantic import BaseModel, Field


class GenerateJiraAuthResponse(BaseModel):
    auth_url: str = Field(
        title="Jira Authorization URL",
        description="The URL for the Jira authorization page",
    )


class CompleteJiraAuthResponse(BaseModel):
    success: bool = Field(
        title="Success",
        description="Whether the Jira authorization was successful",
    )
    email: str = Field(
        title="User Email",
        description="The Atlassian email resolved from the OAuth token. Use this as user_id in all Jira tool calls.",
    )
    message: str = Field(
        title="Message",
        description="A message describing the authorization status",
    )
