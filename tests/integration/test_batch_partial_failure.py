"""Integration test: Batch with partial failures (Scenario 12)."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image


def test_batch_partial_failure(tmp_path: Path, mock_gemini_success: MagicMock) -> None:
    """Test that batch processing continues despite individual failures."""
    os.environ["GEMINI_API_KEY"] = "test_key"

    from src.cli.main import main
    from src.models.exceptions import APIError

    call_count = 0

    def side_effect_fail_second(*args: object, **kwargs: object) -> MagicMock:
        """Fail on second call, succeed on others."""
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            raise APIError("Simulated API failure")
        return mock_gemini_success

    output_path = tmp_path / "test.png"

    with patch("src.services.gemini_service.genai.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = side_effect_fail_second
        mock_client_class.return_value = mock_client

        exit_code = main(["--prompt", "Test", "--out", str(output_path), "--batch", "3"])

    # Verify exit code is 0 (success because some succeeded)
    assert exit_code == 0

    # Verify 2 files created (1st and 3rd succeeded)
    assert (tmp_path / "test_1.png").exists()
    assert not (tmp_path / "test_2.png").exists()  # This one failed
    assert (tmp_path / "test_3.png").exists()

    # Verify successful files are valid PNGs
    for filename in ["test_1.png", "test_3.png"]:
        img = Image.open(tmp_path / filename)
        assert img.format == "PNG"
        img.close()
