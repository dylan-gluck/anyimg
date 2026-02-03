"""Configuration model for image generation."""

import os
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from .exceptions import (
    InvalidBatchCountError,
    InvalidInputImageError,
    MissingAPIKeyError,
    TooManyInputImagesError,
)


class GenerationConfig(BaseModel):
    """Validates and stores CLI configuration from user arguments."""

    prompt: str = Field(..., description="Text prompt for image generation")
    input_images: list[Path] = Field(
        default_factory=list, description="List of 0-3 input image paths"
    )
    output_path: Path | None = Field(
        default=None, description="Custom output path (None for timestamped default)"
    )
    batch_count: int = Field(default=1, ge=1, description="Number of images to generate")
    api_key: str = Field(..., description="Gemini API key from environment")
    aspect_ratio: str | None = Field(
        default=None,
        description="Aspect ratio for generated image (e.g., '1:1', '16:9')",
    )
    resolution: str | None = Field(
        default=None,
        description="Resolution for generated image (e.g., '1K', '2K', '4K')",
    )

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        """Validate prompt is non-empty and stripped."""
        v = v.strip()
        if not v:
            raise ValueError("Prompt cannot be empty")
        return v

    @field_validator("input_images")
    @classmethod
    def validate_input_images(cls, v: list[Path]) -> list[Path]:
        """Validate input images: max 3, exist, are files, valid formats."""
        if len(v) > 3:
            raise TooManyInputImagesError(len(v))

        valid_formats = {".png", ".jpg", ".jpeg"}
        for path in v:
            if not path.exists():
                raise InvalidInputImageError(
                    f"Input image not found: {path}",
                    remediation=f"Ensure file exists: {path}",
                )
            if not path.is_file():
                raise InvalidInputImageError(
                    f"Input image is not a file: {path}",
                    remediation=f"Provide a file path, not a directory: {path}",
                )
            if path.suffix.lower() not in valid_formats:
                raise InvalidInputImageError(
                    f"Invalid input image format: {path}. Only PNG and JPEG/JPG are supported.",
                    remediation="Provide PNG or JPEG/JPG images only",
                )

        return v

    @field_validator("batch_count")
    @classmethod
    def validate_batch_count(cls, v: int) -> int:
        """Validate batch count is at least 1."""
        if v < 1:
            raise InvalidBatchCountError(v)
        return v

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key is non-empty."""
        if not v or not v.strip():
            raise MissingAPIKeyError()
        return v

    @classmethod
    def from_args(
        cls,
        prompt: str,
        input_images: list[str] | None = None,
        output_path: str | None = None,
        batch_count: int = 1,
        aspect_ratio: str | None = None,
        resolution: str | None = None,
    ) -> "GenerationConfig":
        """Create config from CLI arguments."""
        api_key = os.getenv("GEMINI_API_KEY", "")

        return cls(
            prompt=prompt,
            input_images=[Path(p) for p in (input_images or [])],
            output_path=Path(output_path) if output_path else None,
            batch_count=batch_count,
            api_key=api_key,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
        )
