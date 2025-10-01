"""Integration test: Batch with custom path (Scenario 4)."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image


def test_batch_with_custom_path(tmp_path: Path, mock_gemini_success: MagicMock) -> None:
    """Test batch generation with custom output path (creates indexed files)."""
    os.environ["GEMINI_API_KEY"] = "test_key"

    from src.cli.main import main

    output_path = tmp_path / "art.png"

    with patch("src.services.gemini_service.genai.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_gemini_success
        mock_client_class.return_value = mock_client

        exit_code = main(["--prompt", "Art", "--out", str(output_path), "--batch", "3"])

    # Verify exit code
    assert exit_code == 0

    # Verify indexed files exist
    assert (tmp_path / "art_1.png").exists()
    assert (tmp_path / "art_2.png").exists()
    assert (tmp_path / "art_3.png").exists()

    # Verify they're valid PNGs
    for i in range(1, 4):
        img = Image.open(tmp_path / f"art_{i}.png")
        assert img.format == "PNG"
        img.close()
