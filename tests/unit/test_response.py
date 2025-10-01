"""Unit tests for ImageGenerationResponse model."""

import pytest

from src.models.response import ImageGenerationResponse


def test_success_requires_non_empty_image_data() -> None:
    """Test: success=True requires non-empty image_data."""
    response = ImageGenerationResponse(
        image_data=b"valid png data",
        success=True,
        error_message=None,
    )
    assert response.success is True
    assert response.image_data == b"valid png data"


def test_success_cannot_have_empty_image_data() -> None:
    """Test: success=True with empty image_data fails validation."""
    with pytest.raises(ValueError, match="non-empty image_data"):
        ImageGenerationResponse(
            image_data=b"",
            success=True,
            error_message=None,
        )


def test_failure_requires_error_message() -> None:
    """Test: success=False requires error_message."""
    response = ImageGenerationResponse(
        image_data=b"",
        success=False,
        error_message="API failed",
    )
    assert response.success is False
    assert response.error_message == "API failed"


def test_failure_cannot_have_empty_error_message() -> None:
    """Test: success=False without error_message fails validation."""
    with pytest.raises(ValueError, match="error_message"):
        ImageGenerationResponse(
            image_data=b"",
            success=False,
            error_message=None,
        )


def test_validation_fails_if_both_success_and_error() -> None:
    """Test: validation fails if both success and error_message present."""
    with pytest.raises(ValueError, match="cannot have error_message"):
        ImageGenerationResponse(
            image_data=b"image data",
            success=True,
            error_message="Should not be here",
        )
