"""Response model for Gemini API image generation."""

from pydantic import BaseModel, Field, model_validator


class ImageGenerationResponse(BaseModel):
    """Wrapper for Gemini API response data."""

    image_data: bytes = Field(..., description="Raw PNG image bytes")
    success: bool = Field(..., description="Whether generation succeeded")
    error_message: str | None = Field(default=None, description="Error details if failed")

    @model_validator(mode="after")
    def validate_response(self) -> "ImageGenerationResponse":
        """Validate response consistency."""
        if self.success:
            if not self.image_data:
                raise ValueError("Success response must have non-empty image_data")
            if self.error_message is not None:
                raise ValueError("Success response cannot have error_message")
        else:
            if not self.error_message:
                raise ValueError("Failed response must have error_message")

        return self
