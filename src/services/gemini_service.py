"""Gemini API service for image generation."""

from typing import Any

from google import genai

from src.models.exceptions import (
    APIError,
    APIRateLimitError,
    APIResponseError,
    APITimeoutError,
    ConfigurationError,
)
from src.models.request import ImageGenerationRequest
from src.models.response import ImageGenerationResponse


class GeminiService:
    """Service for generating images via Gemini API."""

    def __init__(self, client: genai.Client | None = None) -> None:
        """Initialize Gemini service.

        Args:
            client: Optional genai.Client instance for testing. If None, creates new client.
        """
        self.client = client if client is not None else genai.Client()

    def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """Generate image using Gemini API.

        Args:
            request: Image generation request configuration

        Returns:
            ImageGenerationResponse with success/failure status

        Raises:
            APITimeoutError: If request times out
            APIRateLimitError: If rate limit exceeded
            ConfigurationError: If authentication fails
            APIResponseError: If response is invalid
            APIError: For other API failures
        """
        try:
            # Prepare contents: prompt + optional input images
            if request.input_images:
                contents = [request.prompt] + request.input_images
            else:
                contents = request.prompt

            # Call Gemini API
            response = self.client.models.generate_content(
                model=request.model,
                contents=contents,
            )

            # Extract image data from response
            image_data = self._extract_image_data(response)

            return ImageGenerationResponse(
                image_data=image_data,
                success=True,
                error_message=None,
            )

        except TimeoutError as e:
            raise APITimeoutError(timeout=request.timeout) from e
        except APIResponseError:
            # Re-raise our custom exception as-is
            raise
        except Exception as e:
            # Map SDK exceptions to custom exceptions
            error_msg = str(e).lower()

            if "401" in error_msg or "unauthorized" in error_msg or "auth" in error_msg:
                raise ConfigurationError(
                    message="Authentication failed",
                    remediation="Check your GEMINI_API_KEY environment variable",
                ) from e
            elif "429" in error_msg or "rate limit" in error_msg:
                raise APIRateLimitError() from e
            elif "timeout" in error_msg:
                raise APITimeoutError(timeout=request.timeout) from e
            else:
                raise APIError(
                    message=f"API request failed: {str(e)}",
                    remediation="Check your internet connection and retry",
                ) from e

    def _extract_image_data(self, response: Any) -> bytes:
        """Extract image data from Gemini API response.

        Args:
            response: Raw response from Gemini API

        Returns:
            Image data as bytes

        Raises:
            APIResponseError: If no image data found in response
        """
        try:
            # Navigate response structure to find image data
            candidate = response.candidates[0]
            parts = candidate.content.parts

            # Find the first part with inline_data
            for part in parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    return part.inline_data.data

            # No image data found
            raise APIResponseError(
                message="No image data in API response",
                remediation="The API returned a response but no image was generated",
            )

        except (IndexError, AttributeError) as e:
            raise APIResponseError(
                message="Invalid API response structure",
                remediation="The API response format is unexpected",
            ) from e
