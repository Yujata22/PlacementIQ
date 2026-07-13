from pydantic import BaseModel, Field


class AgentChatRequest(BaseModel):
    question: str = Field(
        min_length=3,
        description="Supply-chain planning question from the user.",
    )