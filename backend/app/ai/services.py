import json
import re
import logging
from typing import Optional

from google import genai
from google.genai import errors as genai_errors
from google.api_core.exceptions import (
    GoogleAPICallError,
    InvalidArgument,
    Unauthenticated,
)
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.hardware import HardwareAsset
from app.ai.schemas import ChatbotResponse, DeviceRecommendation

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Base exception for AI service errors."""

    pass


class AIAuthenticationError(AIServiceError):
    """Raised when API credentials are missing or invalid."""

    pass


class AIRateLimitError(AIServiceError):
    """Raised when API rate limit is exceeded."""

    pass


class AITimeoutError(AIServiceError):
    """Raised when API call times out."""

    pass


class DeviceRecommendationService:
    """Service for device recommendation chatbot using Gemini."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the recommendation service with API credentials."""
        self.api_key = api_key or settings.gemini_api_key
        if not self.api_key:
            raise AIAuthenticationError("GEMINI_API_KEY not configured in environment")

        self.client = genai.Client(api_key=self.api_key)
        self.model = settings.gemini_model

    async def _auto_flag_repair_devices(self) -> None:
        """Use AI to scan devices for notes suggesting they need repair, and set a flag for admin review."""
        db = SessionLocal()
        try:
            # Fetch all devices that are not already flagged and have non-empty notes
            devices_to_check = db.query(HardwareAsset).filter(
                HardwareAsset.repair_flagged.is_(False),
                HardwareAsset.notes.isnot(None),
                HardwareAsset.notes != "",
            ).all()

            if not devices_to_check:
                return

            logger.debug(f"Auto-flag: Checking {len(devices_to_check)} devices for repair keywords in notes")

            for device in devices_to_check:
                notes_lower = device.notes.lower()
                # Quick keyword pre-check before calling Gemini
                repair_keywords = [
                    "battery swelling", "liquid damage", "water damage", "cracked screen",
                    "does not work", "broken", "needs repair", "keyboard sticky",
                    "do not issue", "faulty", "not working", "damaged",
                ]
                has_repair_keyword = any(kw in notes_lower for kw in repair_keywords)

                if not has_repair_keyword:
                    continue

                # Use Gemini to confirm if this device should be flagged for repair
                try:
                    prompt = (
                        f"Given this hardware device note, determine if the device needs repair or is unsafe to rent.\n\n"
                        f"Device: {device.name} ({device.brand})\n"
                        f"Notes: {device.notes}\n\n"
                        f"Reply with exactly one word: REPAIR if the device needs repair, OK if it's fine to rent."
                    )
                    response = await self.client.aio.models.generate_content(
                        model=self.model,
                        contents=[prompt],
                    )
                    if response.text and "REPAIR" in response.text.strip().upper():
                        logger.info(f"Auto-flag: Flagging '{device.name}' (ID {device.id}) for admin review — notes: {device.notes}")
                        device.repair_flagged = True
                        db.add(device)
                except Exception as e:
                    logger.warning(f"Auto-flag: Gemini check failed for device {device.id}: {e}")
                    # Fallback: if keyword matched and AI failed, still flag it
                    device.repair_flagged = True
                    db.add(device)

            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Auto-flag: Database error: {e}")
        finally:
            db.close()

    async def chat(
        self,
        user_message: str,
        conversation_history: Optional[list[dict]] = None,
    ) -> ChatbotResponse:
        """
        Process user message and return device recommendations.

        Args:
            user_message: Natural language request from user
            conversation_history: Previous messages for context (optional)

        Returns:
            ChatbotResponse with assistant message and device recommendations

        Raises:
            AIAuthenticationError: If API credentials are invalid
            AIRateLimitError: If rate limit is exceeded
            AITimeoutError: If request times out
            AIServiceError: For other API errors
        """
        logger.debug(f"Processing message: {user_message[:50]}...")
        logger.debug(f"Conversation history length: {len(conversation_history) if conversation_history else 0}")
        logger.debug(f"API Key configured: {bool(self.api_key)}")
        logger.debug(f"API Key preview: {self.api_key[:10]}...{self.api_key[-4:] if len(self.api_key) > 14 else ''}")

        # Auto-flag devices with suspicious notes before fetching available devices
        try:
            await self._auto_flag_repair_devices()
        except Exception as e:
            logger.warning(f"Auto-flag skipped due to error: {e}")

        # Fetch available devices from database (now excludes newly-flagged repair devices)
        available_devices = await self._fetch_available_devices()
        logger.debug(f"Found {len(available_devices)} available devices")

        # Build context for Gemini
        devices_context = self._format_devices_for_context(available_devices)
        prompt = self._build_recommendation_prompt(
            user_message, devices_context, conversation_history
        )

        try:
            # Call Gemini with conversation history
            messages = self._build_message_history(user_message, conversation_history)
            logger.debug(f"Built {len(messages)} messages for history")

            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=messages + [prompt],
            )
            logger.debug(f"Got response from Gemini: {response.text[:100] if response.text else 'None'}...")

            if not response.text:
                raise AIServiceError("Empty response from Gemini API")

            # Parse response to extract recommendations
            assistant_message, recommended_ids = self._parse_response(
                response.text, available_devices
            )

            # Build recommendations from database
            recommendations = [
                DeviceRecommendation(
                    id=device.id,
                    name=device.name,
                    brand=device.brand,
                    status=device.status,
                    reason=self._get_recommendation_reason(
                        device, user_message, recommended_ids
                    ),
                )
                for device in available_devices
                if device.id in recommended_ids
            ]

            return ChatbotResponse(
                message=assistant_message,
                recommendations=recommendations,
                conversation_context=user_message,
            )

        except Unauthenticated as e:
            raise AIAuthenticationError(
                f"Invalid or expired API credentials: {str(e)}"
            ) from e

        except genai_errors.ClientError as e:
            # Modern genai SDK raises ClientError for 4xx responses (including quota/rate limits)
            error_body = str(e)
            error_lower = error_body.lower()
            if "429" in error_body or "rate limit" in error_lower or "quota" in error_lower or "resource_exhausted" in error_lower:
                raise AIRateLimitError(f"API rate limit or quota exceeded: {str(e)}") from e
            if "401" in error_body or "invalid api key" in error_lower or "unauthenticated" in error_lower:
                raise AIAuthenticationError(f"API authentication failed: {str(e)}") from e
            raise AIServiceError(f"Gemini API client error: {str(e)}") from e

        except InvalidArgument as e:
            error_msg = str(e).lower()
            if "api key" in error_msg or "api_key" in error_msg or "invalid argument" in error_msg:
                raise AIAuthenticationError(f"Invalid API key: {str(e)}") from e
            if "rate limit" in error_msg:
                raise AIRateLimitError(f"API rate limit exceeded: {str(e)}") from e
            raise AIServiceError(f"Invalid request to Gemini API: {str(e)}") from e

        except GoogleAPICallError as e:
            error_msg = str(e).lower()
            if "timeout" in error_msg or "deadline" in error_msg:
                raise AITimeoutError(f"API request timed out: {str(e)}") from e
            if "rate limit" in error_msg:
                raise AIRateLimitError(f"API rate limit exceeded: {str(e)}") from e
            if "api key" in error_msg or "apikey" in error_msg or "invalid argument" in error_msg:
                raise AIAuthenticationError(f"Invalid API key: {str(e)}") from e
            raise AIServiceError(f"Gemini API error: {str(e)}") from e

        except ValueError as e:
            raise AIServiceError(f"Response parsing failed: {str(e)}") from e

        except Exception as e:
            raise AIServiceError(f"Unexpected error: {type(e).__name__}: {str(e)}") from e

    async def _fetch_available_devices(self) -> list[HardwareAsset]:
        """Fetch all available devices from the database."""
        db = SessionLocal()
        try:
            devices = db.query(HardwareAsset).filter(
                HardwareAsset.status == "Available"
            ).all()
            return devices
        finally:
            db.close()

    def _format_devices_for_context(self, devices: list[HardwareAsset]) -> str:
        """Format available devices for inclusion in the prompt."""
        if not devices:
            return "No devices currently available."

        devices_list = []
        for device in devices:
            device_info = f"ID: {device.id}, Name: {device.name}, Brand: {device.brand}"
            if device.notes:
                device_info += f", Notes: {device.notes}"
            devices_list.append(device_info)

        return "\n".join(devices_list)

    def _build_recommendation_prompt(
        self,
        user_message: str,
        devices_context: str,
        conversation_history: Optional[list[dict]] = None,
    ) -> str:
        """Build the prompt for Gemini to generate recommendations."""

        history_context = ""
        if conversation_history:
            history_context = "\nPrevious conversation context:\n"
            for msg in conversation_history[-3:]:  # Last 3 messages for context
                history_context += f"- {msg.get('role', 'unknown')}: {msg.get('content', '')[:100]}...\n"

        prompt = f"""
You are a helpful hardware rental assistant. Your job is to help users find the perfect device for their needs.

Available Devices:
{devices_context}

User Request: {user_message}
{history_context}

Based on the user's request and the available devices, provide:
1. A friendly, conversational response explaining your recommendations
2. The device IDs you recommend (format: "Recommended IDs: [1, 3, 5]" at the end)

Consider the user's specific needs, use case, and preferences. Be helpful and suggest alternatives if exact matches aren't available.
If no devices match, explain why and suggest what they might look for in the future.

IMPORTANT: Do not use markdown formatting (no *bold*, no - bullets, no # headers). Use plain text only.
"""
        return prompt.strip()

    def _build_message_history(self, user_message: str, conversation_history: Optional[list[dict]] = None) -> list:
        """Build message history for multi-turn conversation."""
        from google.genai import types
        
        messages = []
        if conversation_history:
            for msg in conversation_history:
                role = msg.get("role", "user")
                # Convert assistant to model for Gemini API
                if role == "assistant":
                    role = "model"
                messages.append(types.Content(role=role, parts=[types.Part(text=msg.get("content", ""))]))
        return messages

    def _parse_response(self, response_text: str, available_devices: list[HardwareAsset]) -> tuple[str, list[int]]:
        """Parse Gemini response to extract message and recommended device IDs."""
        # Extract recommended IDs from response
        recommended_ids = []
        lines = response_text.split("\n")
        for line in lines:
            if "Recommended IDs:" in line or "recommended IDs:" in line:
                # Extract numbers from the line
                ids_match = re.findall(r"\d+", line)
                recommended_ids = [int(id_str) for id_str in ids_match]
                break

        # Remove the IDs line from the message
        message_lines = [
            line for line in lines
            if "Recommended IDs:" not in line and "recommended IDs:" not in line
        ]
        assistant_message = "\n".join(message_lines).strip()

        return assistant_message, recommended_ids

    def _get_recommendation_reason(
        self, device: HardwareAsset, user_message: str, recommended_ids: list[int]
    ) -> str:
        """Generate a reason why this device was recommended."""
        # Simple heuristic: match keywords from user message to device attributes
        user_lower = user_message.lower()
        device_name_lower = device.name.lower()
        device_brand_lower = device.brand.lower()

        if any(keyword in user_lower for keyword in ["camera", "photo", "video"]):
            if any(phone in device_name_lower for phone in ["iphone", "galaxy", "pixel"]):
                return "Great camera capabilities for photography and video"

        if any(keyword in user_lower for keyword in ["laptop", "work", "coding", "development"]):
            if any(laptop in device_name_lower for laptop in ["macbook", "xps", "thinkpad"]):
                return "Powerful performance for development and productivity"

        if any(keyword in user_lower for keyword in ["audio", "music", "sound"]):
            if any(audio in device_name_lower for audio in ["headphone", "earphone", "speaker"]):
                return "Excellent audio quality for music and content consumption"

        return "Matches your requirements and is currently available"

