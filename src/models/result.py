"""Result model for batch processing tracking."""

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field


class GenerationResult(BaseModel):
    """Represents the outcome of a single generation attempt (used in batch processing)."""

    index: int = Field(..., description="Batch index (0-based)")
    output_path: Path = Field(..., description="Where image was/would be saved")
    success: bool = Field(..., description="Whether this attempt succeeded")
    error_message: str | None = Field(default=None, description="Error details if failed")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When generation was attempted"
    )
