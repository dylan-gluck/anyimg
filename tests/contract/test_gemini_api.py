"""Contract tests for Gemini API integration."""

from unittest.mock import MagicMock

import pytest
from PIL import Image

from src.models.exceptions import (
    APIResponseError,
    APITimeoutError,
    ConfigurationError,
)
from src.models.request import ImageGenerationRequest
from src.services.gemini_service import GeminiService


def test_generate_single_image_success(
    mock_genai_client: MagicMock, mock_success_response: MagicMock
) -> None:
    """Test ID: test_generate_single_image_success.

    Mock: client.models.generate_content returns valid PNG response
    Assert: correct model and prompt passed to API
    Assert: returns ImageGenerationResponse(success=True) with valid image_data
    """
    mock_genai_client.models.generate_content.return_value = mock_success_response

    service = GeminiService(client=mock_genai_client)
    request = ImageGenerationRequest(
        model="gemini-2.5-flash-image-preview",
        prompt="A blue sky",
        input_images=[],
        timeout=60,
    )

    response = service.generate_image(request)

    # Assert correct parameters passed
    mock_genai_client.models.generate_content.assert_called_once()
    call_kwargs = mock_genai_client.models.generate_content.call_args.kwargs
    assert call_kwargs["model"] == "gemini-2.5-flash-image-preview"
    assert "A blue sky" in str(call_kwargs["contents"])

    # Assert successful response
    assert response.success is True
    assert isinstance(response.image_data, bytes)
    assert len(response.image_data) > 0


def test_generate_multimodal_success(
    mock_genai_client: MagicMock,
    mock_success_response: MagicMock,
    sample_pil_images: list[Image.Image],
) -> None:
    """Test ID: test_generate_multimodal_success.

    Mock: API receives prompt + 2 PIL Images
    Assert: contents parameter is list with 3 elements
    Assert: returns successful response with image data
    """
    mock_genai_client.models.generate_content.return_value = mock_success_response

    service = GeminiService(client=mock_genai_client)
    request = ImageGenerationRequest(
        model="gemini-2.5-flash-image-preview",
        prompt="Combine these styles",
        input_images=sample_pil_images[:2],
        timeout=60,
    )

    response = service.generate_image(request)

    # Assert contents is a list with prompt + images
    call_kwargs = mock_genai_client.models.generate_content.call_args.kwargs
    contents = call_kwargs["contents"]
    assert isinstance(contents, list)
    assert len(contents) == 3  # prompt + 2 images

    assert response.success is True
    assert len(response.image_data) > 0


def test_generate_timeout_error(
    mock_genai_client: MagicMock, mock_timeout_error: Exception
) -> None:
    """Test ID: test_generate_timeout_error.

    Mock: API call raises timeout exception after 60 seconds
    Assert: raises APITimeoutError with helpful message
    """
    mock_genai_client.models.generate_content.side_effect = mock_timeout_error

    service = GeminiService(client=mock_genai_client)
    request = ImageGenerationRequest(
        model="gemini-2.5-flash-image-preview",
        prompt="A landscape",
        input_images=[],
        timeout=60,
    )

    with pytest.raises(APITimeoutError) as exc_info:
        service.generate_image(request)

    assert "60 seconds" in str(exc_info.value)


def test_generate_auth_error(mock_genai_client: MagicMock, mock_auth_error: Exception) -> None:
    """Test ID: test_generate_auth_error.

    Mock: API raises 401 authentication error
    Assert: raises ConfigurationError with API key setup instructions
    """
    mock_genai_client.models.generate_content.side_effect = mock_auth_error

    service = GeminiService(client=mock_genai_client)
    request = ImageGenerationRequest(
        model="gemini-2.5-flash-image-preview",
        prompt="Test",
        input_images=[],
        timeout=60,
    )

    with pytest.raises(ConfigurationError) as exc_info:
        service.generate_image(request)

    error_msg = str(exc_info.value).lower()
    assert "api" in error_msg or "key" in error_msg or "auth" in error_msg


def test_generate_rate_limit_error(
    mock_genai_client: MagicMock,
) -> None:
    """Test ID: test_generate_rate_limit_error.

    Mock: API raises 429 rate limit error
    Assert: raises APIRateLimitError with retry suggestion
    """
    from src.models.exceptions import APIRateLimitError

    rate_limit_error = Exception("429 Too Many Requests")
    mock_genai_client.models.generate_content.side_effect = rate_limit_error

    service = GeminiService(client=mock_genai_client)
    request = ImageGenerationRequest(
        model="gemini-2.5-flash-image-preview",
        prompt="An image",
        input_images=[],
        timeout=60,
    )

    with pytest.raises(APIRateLimitError):
        service.generate_image(request)


def test_generate_empty_response(mock_genai_client: MagicMock) -> None:
    """Test ID: test_generate_empty_response.

    Mock: API returns Response with no inline_data
    Assert: raises APIResponseError indicating no image data
    """
    # Mock response with no inline_data
    empty_response = MagicMock()
    empty_part = MagicMock()
    empty_part.inline_data = None

    empty_candidate = MagicMock()
    empty_candidate.content.parts = [empty_part]

    empty_response.candidates = [empty_candidate]

    mock_genai_client.models.generate_content.return_value = empty_response

    service = GeminiService(client=mock_genai_client)
    request = ImageGenerationRequest(
        model="gemini-2.5-flash-image-preview",
        prompt="Generate something",
        input_images=[],
        timeout=60,
    )

    with pytest.raises(APIResponseError):
        service.generate_image(request)


def test_generate_max_input_images(
    mock_genai_client: MagicMock,
    mock_success_response: MagicMock,
    sample_pil_images: list[Image.Image],
) -> None:
    """Test ID: test_generate_max_input_images.

    Mock: API receives prompt + 3 PIL Images
    Assert: contents list has 4 elements (prompt + 3 images)
    Assert: returns successful response
    """
    mock_genai_client.models.generate_content.return_value = mock_success_response

    service = GeminiService(client=mock_genai_client)
    request = ImageGenerationRequest(
        model="gemini-2.5-flash-image-preview",
        prompt="Mix these styles",
        input_images=sample_pil_images,  # All 3 images
        timeout=60,
    )

    response = service.generate_image(request)

    # Assert contents has 4 elements
    call_kwargs = mock_genai_client.models.generate_content.call_args.kwargs
    contents = call_kwargs["contents"]
    assert len(contents) == 4  # prompt + 3 images

    assert response.success is True
