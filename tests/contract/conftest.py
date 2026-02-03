"""Pytest fixtures for contract tests."""

from unittest.mock import MagicMock

import pytest
from PIL import Image


@pytest.fixture
def mock_genai_client() -> MagicMock:
    """Mock genai.Client() for testing."""
    client = MagicMock()
    return client


@pytest.fixture
def mock_success_response() -> MagicMock:
    """Valid Response with PNG bytes."""
    img = Image.new("RGB", (100, 100), color="blue")

    # Mock response structure with new API (parts property)
    response = MagicMock()
    part = MagicMock()
    part.text = None
    part.as_image.return_value = img

    response.parts = [part]

    return response


@pytest.fixture
def mock_timeout_error() -> Exception:
    """Simulates timeout exception."""
    return TimeoutError("Request timed out")


@pytest.fixture
def mock_rate_limit_error() -> Exception:
    """Simulates 429 error."""

    class RateLimitError(Exception):
        pass

    return RateLimitError("429 Too Many Requests")


@pytest.fixture
def mock_auth_error() -> Exception:
    """Simulates 401 error."""

    class AuthError(Exception):
        pass

    return AuthError("401 Unauthorized")


@pytest.fixture
def sample_pil_images() -> list[Image.Image]:
    """Creates test PIL.Image objects."""
    images = []
    for i in range(3):
        img = Image.new("RGB", (50, 50), color=["red", "green", "blue"][i])
        images.append(img)
    return images
