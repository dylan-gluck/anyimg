"""Integration test: Batch with default naming (Scenario 5)."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image


def test_batch_with_default_naming(tmp_path: Path, mock_gemini_success: MagicMock) -> None:
    """Test batch generation with default timestamped naming."""
    os.environ["GEMINI_API_KEY"] = "test_key"

    from src.cli.main import main

    # Change to temp directory for output
    original_cwd = Path.cwd()
    os.chdir(tmp_path)

    try:
        with patch("src.services.gemini_service.genai.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.models.generate_content.return_value = mock_gemini_success
            mock_client_class.return_value = mock_client

            exit_code = main(["--prompt", "Patterns", "--batch", "3"])

        # Verify exit code
        assert exit_code == 0

        # Find generated files with anyimg_ prefix
        generated_files = list(tmp_path.glob("anyimg_*.png"))
        assert len(generated_files) == 3

        # Verify unique filenames
        filenames = [f.name for f in generated_files]
        assert len(set(filenames)) == 3

        # Verify they're valid PNGs
        for file in generated_files:
            img = Image.open(file)
            assert img.format == "PNG"
            img.close()

    finally:
        os.chdir(original_cwd)
