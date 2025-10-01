"""Integration test: basic text-to-image (Scenario 1)."""

import os
from pathlib import Path
from typing import Any
from unittest.mock import patch

from PIL import Image
from pytest import MonkeyPatch

from src.cli.main import main


def test_basic_text_to_image(
    tmp_path: Path, mock_gemini_success: Any, monkeypatch: MonkeyPatch
) -> None:
    """Test basic text-to-image generation with default output.

    Scenario 1: Given the user provides only a text prompt,
    When they run the CLI tool,
    Then an image is generated and saved as anyimg_<timestamp>.png
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GEMINI_API_KEY", "test_api_key")

    with patch("src.services.gemini_service.genai.Client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.models.generate_content.return_value = mock_gemini_success

        exit_code = main(["--prompt", "A serene mountain landscape"])

        assert exit_code == 0

        # Check that a file was created
        generated_files = list(tmp_path.glob("anyimg_*.png"))
        assert len(generated_files) == 1

        # Verify it's a valid PNG
        img = Image.open(generated_files[0])
        assert img.format == "PNG"
        img.close()
