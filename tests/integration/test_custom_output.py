"""Integration test: custom output path (Scenario 3)."""

import os
from pathlib import Path
from typing import Any
from unittest.mock import patch

from PIL import Image
from pytest import MonkeyPatch

from src.cli.main import main


def test_custom_output_path(
    tmp_path: Path, mock_gemini_success: Any, monkeypatch: MonkeyPatch
) -> None:
    """Test custom output path with directory creation.

    Scenario 3: Given the user specifies a custom output path,
    When they run the CLI tool,
    Then the image is saved to that exact path (creating directories if needed)
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GEMINI_API_KEY", "test_api_key")

    output_path = tmp_path / "outputs" / "city.png"

    with patch("src.services.gemini_service.genai.Client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.models.generate_content.return_value = mock_gemini_success

        exit_code = main(["--prompt", "City", "--out", str(output_path)])

        assert exit_code == 0
        assert output_path.exists()
        assert output_path.parent.exists()  # outputs/ directory created

        # Verify it's a valid PNG
        img = Image.open(output_path)
        assert img.format == "PNG"
        img.close()
