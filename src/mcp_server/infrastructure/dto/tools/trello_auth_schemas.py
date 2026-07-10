from pydantic import BaseModel, Field


class GenerateTrelloAuthResponse(BaseModel):
    auth_url: str = Field(
        title="Trello Authorization URL",
        description="The URL for the Trello authorization page",
    )


class CompleteTrelloAuthResponse(BaseModel):
    success: bool = Field(
        title="Success",
        description="Whether the Trello token storage was successful",
    )
    user_id: str = Field(
        title="User ID",
        description="The user ID the tokens were stored for",
    )
    message: str = Field(
        title="Message",
        description="A message describing the authorization status",
    )
