"""Integration test: Invalid batch count (Scenario 13)."""

import os
from pathlib import Path

from src.cli.main import main


def test_invalid_batch_count(tmp_path: Path) -> None:
    """Test that batch count of 0 raises validation error."""
    os.environ["GEMINI_API_KEY"] = "test_key"

    exit_code = main(["--prompt", "Test", "--out", str(tmp_path / "out.png"), "--batch", "0"])

    # Verify validation error exit code
    assert exit_code == 2

    # Verify no output file created
    assert not (tmp_path / "out.png").exists()
