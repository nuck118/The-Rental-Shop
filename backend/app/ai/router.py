from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field

from app.ai.services import (
    DeviceRecommendationService,
    AIAuthenticationError,
    AIRateLimitError,
    AITimeoutError,
    AIServiceError,
)
from app.ai.schemas import ChatbotResponse, ChatMessage

router = APIRouter(prefix="/api/ai", tags=["AI Chatbot"])


class ChatRequest(BaseModel):
    """Request schema for chatbot messages."""

    message: str = Field(..., min_length=1, max_length=2000)
    conversation_history: list[ChatMessage] = Field(
        default_factory=list,
        description="Previous messages in the conversation",
    )


def get_recommendation_service() -> DeviceRecommendationService:
    """Dependency injection for recommendation service."""
    return DeviceRecommendationService()


@router.post(
    "/chat",
    response_model=ChatbotResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat with device recommendation assistant",
    description="Get device recommendations based on natural language request",
)
async def chat_with_assistant(
    request: ChatRequest,
    service: DeviceRecommendationService = Depends(get_recommendation_service),
) -> ChatbotResponse:
    """
    Chat with the AI assistant to get device recommendations.

    The assistant understands natural language requests and recommends available
    devices that match your needs.

    **Request Body:**
    - `message`: Your natural language request (e.g., "I need a phone with a great camera")
    - `conversation_history`: Previous messages for context (optional)

    **Response:**
    - `message`: Assistant's conversational response
    - `recommendations`: List of recommended devices with reasons
    - `conversation_context`: Context for multi-turn conversations

    **Example Request:**
    ```json
    {
      "message": "I need a laptop for software development",
      "conversation_history": []
    }
    ```

    **Example Response:**
    ```json
    {
      "message": "Great! For software development, I'd recommend...",
      "recommendations": [
        {
          "id": 2,
          "name": "Apple MacBook Pro 13",
          "brand": "Apple",
          "status": "Available",
          "reason": "Powerful performance for development and productivity"
        }
      ],
      "conversation_context": "I need a laptop for software development"
    }
    ```

    **Error Responses:**
    - `401 Unauthorized`: API credentials not configured
    - `429 Too Many Requests`: API rate limit exceeded
    - `504 Gateway Timeout`: API request timed out
    - `500 Internal Server Error`: Other API or processing errors
    """

    try:
        # Convert ChatMessage objects to dicts for service
        history = [
            {"role": msg.role.value, "content": msg.content}
            for msg in request.conversation_history
        ]

        response = await service.chat(
            user_message=request.message,
            conversation_history=history if history else None,
        )

        return response

    except AIAuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"AI service authentication failed: {str(e)}",
        ) from e

    except AIRateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"AI service rate limit exceeded: {str(e)}",
        ) from e

    except AITimeoutError as e:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"AI service request timed out: {str(e)}",
        ) from e

    except AIServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}",
        ) from e


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Check AI service health",
    description="Verify that the AI service is properly configured",
)
async def check_ai_health(
    service: DeviceRecommendationService = Depends(get_recommendation_service),
) -> dict:
    """
    Check if the AI service is properly configured and ready.

    Returns:
    - `status`: "healthy" if service is ready, "unhealthy" otherwise
    - `model`: The configured Gemini model name
    - `message`: Status message
    """

    try:
        return {
            "status": "healthy",
            "model": service.model,
            "message": "AI chatbot service is ready",
        }
    except AIAuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"AI service not configured: {str(e)}",
        ) from e
