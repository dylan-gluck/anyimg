"""Integration test: invalid input format (Scenario 7)."""

import subprocess
from pathlib import Path

from pytest import MonkeyPatch


def test_invalid_input_format(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """Test rejection of invalid input image format.

    Scenario 7: Given a non-image file is provided as input,
    When they run the CLI tool,
    Then an error message is shown with exit code 2 (validation error)
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GEMINI_API_KEY", "test_api_key")

    # Create a non-image file
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("not an image")

    result = subprocess.run(
        ["uv", "run", "python", "-m", "src", "--prompt", "Test", "--in", str(txt_file)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2  # Validation error
    assert "Invalid input image format" in result.stderr or "invalid" in result.stderr.lower()
