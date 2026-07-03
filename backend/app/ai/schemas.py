from enum import Enum
from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class DeviceRecommendation(BaseModel):
    """A recommended device from the database."""

    id: int = Field(..., description="Device ID")
    name: str = Field(..., description="Device name/model")
    brand: str = Field(..., description="Device brand")
    status: str = Field(..., description="Current availability status")
    reason: str = Field(..., description="Why this device matches the user's needs")


class ChatMessage(BaseModel):
    """A single message in the chat conversation."""

    role: MessageRole = Field(..., description="Message sender (user or assistant)")
    content: str = Field(..., description="Message text content")


class ChatbotResponse(BaseModel):
    """Response from the chatbot assistant."""

    message: str = Field(..., description="Assistant's response to the user")
    recommendations: list[DeviceRecommendation] = Field(
        default_factory=list,
        description="List of recommended devices matching user needs",
    )
    conversation_context: str = Field(
        default="",
        description="Internal context for multi-turn conversations",
    )
