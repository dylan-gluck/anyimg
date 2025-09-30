"""Request model for Gemini API image generation."""

from PIL import Image
from pydantic import BaseModel, Field


class ImageGenerationRequest(BaseModel):
    """Encapsulates a single generation request to Gemini API."""

    model: str = Field(
        default="gemini-2.5-flash-image-preview",
        description="Model identifier for Gemini API",
    )
    prompt: str = Field(..., description="Text prompt for image generation")
    input_images: list[Image.Image] = Field(
        default_factory=list, description="Opened PIL Image objects (0-3)"
    )
    timeout: int = Field(default=60, description="Request timeout in seconds")

    class Config:
        arbitrary_types_allowed = True
