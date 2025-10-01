"""Integration test: Missing input file (Scenario 9)."""

import os
from pathlib import Path

from src.cli.main import main


def test_missing_input_file(tmp_path: Path) -> None:
    """Test that non-existent input image file raises validation error."""
    os.environ["GEMINI_API_KEY"] = "test_key"

    nonexistent_file = tmp_path / "nonexistent.png"
    assert not nonexistent_file.exists()

    exit_code = main(
        [
            "--prompt",
            "Test",
            "--in",
            str(nonexistent_file),
            "--out",
            str(tmp_path / "out.png"),
        ]
    )

    # Verify validation error exit code
    assert exit_code == 2

    # Verify no output file created
    assert not (tmp_path / "out.png").exists()
