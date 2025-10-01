"""Integration test: Multimodal generation (Scenario 2)."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image

from src.cli.main import main


def test_multimodal_generation(
    tmp_path: Path, temp_test_images: list[Path], mock_gemini_success: MagicMock
) -> None:
    """Test image generation with prompt and 2 input images."""
    # Set up API key
    os.environ["GEMINI_API_KEY"] = "test_key"

    # Use first 2 test images
    input1, input2 = temp_test_images[0], temp_test_images[1]

    # Set up output path
    output_path = tmp_path / "combined.png"

    # Mock the Gemini client
    with patch("src.services.gemini_service.genai.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_gemini_success
        mock_client_class.return_value = mock_client

        # Run CLI
        exit_code = main(
            [
                "--prompt",
                "Combine styles",
                "--in",
                f"{input1},{input2}",
                "--out",
                str(output_path),
            ]
        )

    # Verify exit code
    assert exit_code == 0

    # Verify output file exists
    assert output_path.exists()

    # Verify it's a valid PNG
    img = Image.open(output_path)
    assert img.format == "PNG"
    img.close()

    # Verify API was called with correct number of contents (prompt + 2 images)
    call_args = mock_client.models.generate_content.call_args
    contents = call_args.kwargs.get("contents") or call_args[1]
    # Should be a list with prompt + 2 PIL images
    assert isinstance(contents, list)
    assert len(contents) == 3  # prompt + 2 images
