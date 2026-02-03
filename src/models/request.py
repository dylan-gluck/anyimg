"""Request model for Gemini API image generation."""

from typing import Any

from pydantic import BaseModel, Field


class ImageGenerationRequest(BaseModel):
    """Encapsulates a single generation request to Gemini API."""

    model: str = Field(
        default="gemini-3-pro-image-preview",
        description="Model identifier for Gemini API",
    )
    prompt: str = Field(..., description="Text prompt for image generation")
    input_images: list[Any] = Field(  # Using Any for PIL.Image due to Pydantic limitations
        default_factory=list, description="Opened PIL Image objects (0-3)"
    )
    timeout: int = Field(default=60, description="Request timeout in seconds")
    aspect_ratio: str | None = Field(
        default=None,
        description="Aspect ratio for generated image (e.g., '1:1', '16:9')",
    )
    resolution: str | None = Field(
        default=None,
        description="Resolution for generated image (e.g., '1K', '2K', '4K')",
    )

    class Config:
        arbitrary_types_allowed = True
