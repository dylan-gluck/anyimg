"""Shared fixtures for integration tests."""

from io import BytesIO
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
from PIL import Image


@pytest.fixture
def temp_test_images(tmp_path: Path) -> list[Path]:
    """Create temporary test images."""
    images = []
    for i in range(4):
        img_path = tmp_path / f"test_image_{i}.png"
        img = Image.new("RGB", (50, 50), color=["red", "green", "blue", "yellow"][i])
        img.save(img_path)
        images.append(img_path)
    return images


@pytest.fixture
def mock_gemini_success() -> Any:
    """Mock successful Gemini API response."""
    # Create a valid PNG image
    img = Image.new("RGB", (100, 100), color="blue")
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    png_data = img_bytes.getvalue()

    # Mock response structure
    response = MagicMock()
    part = MagicMock()
    part.inline_data.data = png_data

    candidate = MagicMock()
    candidate.content.parts = [part]

    response.candidates = [candidate]

    return response
