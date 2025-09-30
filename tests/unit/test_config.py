"""Unit tests for GenerationConfig model."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.models.config import GenerationConfig
from src.models.exceptions import (
    InvalidBatchCountError,
    InvalidInputImageError,
    MissingAPIKeyError,
    TooManyInputImagesError,
)


def test_prompt_validation_non_empty() -> None:
    """Test: prompt validation (non-empty, stripped)."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}):
        config = GenerationConfig(
            prompt="  Valid prompt  ",
            api_key="test_key",
        )
        assert config.prompt == "Valid prompt"


def test_prompt_validation_empty() -> None:
    """Test: prompt cannot be empty."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}):
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            GenerationConfig(
                prompt="   ",
                api_key="test_key",
            )


def test_max_3_input_images(tmp_path: Path) -> None:
    """Test: max 3 input images (TooManyInputImagesError on 4)."""
    # Create 4 test image files
    images = []
    for i in range(4):
        img_path = tmp_path / f"test{i}.png"
        img_path.write_bytes(b"fake png data")
        images.append(img_path)

    with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}):
        with pytest.raises(TooManyInputImagesError) as exc_info:
            GenerationConfig(
                prompt="Test",
                input_images=images,
                api_key="test_key",
            )
        assert "4" in str(exc_info.value)


def test_batch_count_minimum() -> None:
    """Test: batch_count >= 1 (ValidationError on 0)."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}):
        # Pydantic's Field validator catches this before our custom validator
        with pytest.raises(ValueError, match="greater than or equal"):
            GenerationConfig(
                prompt="Test",
                batch_count=0,
                api_key="test_key",
            )


def test_input_image_file_existence(tmp_path: Path) -> None:
    """Test: input image file existence (InvalidInputImageError)."""
    nonexistent = tmp_path / "nonexistent.png"

    with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}):
        with pytest.raises(InvalidInputImageError, match="not found"):
            GenerationConfig(
                prompt="Test",
                input_images=[nonexistent],
                api_key="test_key",
            )


def test_input_image_format_validation(tmp_path: Path) -> None:
    """Test: input image format validation (.png, .jpg, .jpeg only)."""
    # Create valid formats
    png_path = tmp_path / "test.png"
    png_path.write_bytes(b"fake png")
    jpg_path = tmp_path / "test.jpg"
    jpg_path.write_bytes(b"fake jpg")
    jpeg_path = tmp_path / "test.jpeg"
    jpeg_path.write_bytes(b"fake jpeg")

    with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}):
        config = GenerationConfig(
            prompt="Test",
            input_images=[png_path, jpg_path, jpeg_path],
            api_key="test_key",
        )
        assert len(config.input_images) == 3

    # Test invalid format
    txt_path = tmp_path / "test.txt"
    txt_path.write_bytes(b"fake txt")

    with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}):
        with pytest.raises(InvalidInputImageError, match="Invalid input image format"):
            GenerationConfig(
                prompt="Test",
                input_images=[txt_path],
                api_key="test_key",
            )


def test_missing_api_key() -> None:
    """Test: missing GEMINI_API_KEY (MissingAPIKeyError)."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(MissingAPIKeyError):
            GenerationConfig.from_args(prompt="Test")
