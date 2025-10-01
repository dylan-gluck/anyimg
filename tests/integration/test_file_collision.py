"""Integration test: File collision auto-rename (Scenario 6)."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image


def test_file_collision_auto_rename(tmp_path: Path, mock_gemini_success: MagicMock) -> None:
    """Test that existing files are not overwritten; new files get numeric suffix."""
    os.environ["GEMINI_API_KEY"] = "test_key"

    from src.cli.main import main

    # Create existing file
    existing_file = tmp_path / "myimage.png"
    existing_file.write_text("existing content")
    original_size = existing_file.stat().st_size

    output_path = tmp_path / "myimage.png"

    with patch("src.services.gemini_service.genai.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_gemini_success
        mock_client_class.return_value = mock_client

        exit_code = main(["--prompt", "New image", "--out", str(output_path)])

    # Verify exit code
    assert exit_code == 0

    # Verify original file untouched
    assert existing_file.exists()
    assert existing_file.stat().st_size == original_size

    # Verify new file created with _1 suffix
    renamed_file = tmp_path / "myimage_1.png"
    assert renamed_file.exists()

    # Verify it's a valid PNG
    img = Image.open(renamed_file)
    assert img.format == "PNG"
    img.close()
