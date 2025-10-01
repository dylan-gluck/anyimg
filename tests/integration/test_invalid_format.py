"""Integration test: invalid input format (Scenario 7)."""

import os
from pathlib import Path

from pytest import MonkeyPatch

from src.cli.main import main


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

    exit_code = main(["--prompt", "Test", "--in", str(txt_file)])

    assert exit_code == 2  # Validation error
