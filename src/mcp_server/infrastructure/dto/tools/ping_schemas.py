from pydantic import BaseModel, Field


class PingResult(BaseModel):
    """Response from the ping health-check tool."""

    message: str = Field(description="Fixed value 'pong' confirming the server is alive")
