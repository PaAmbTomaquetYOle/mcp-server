from pydantic import BaseModel, Field


class GenerateSlackAuthResponse(BaseModel):
    auth_url: str = Field(
        title="Slack Authorization URL",
        description="The URL for the Slack OAuth 2.0 authorization page",
    )


class CompleteSlackAuthResponse(BaseModel):
    success: bool = Field(
        title="Success",
        description="Whether the Slack authorization was successful",
    )
    slack_user_id: str = Field(
        title="Slack User ID",
        description="The Slack user ID resolved from the OAuth token. Use this as user_id in search_slack_workspace.",
    )
    team_id: str = Field(
        title="Slack Team ID",
        description="The Slack workspace (team) ID the user authorized.",
    )
    message: str = Field(
        title="Message",
        description="A message describing the authorization status",
    )
