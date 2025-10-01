"""Integration test: Too many input images (Scenario 8)."""

import os
from pathlib import Path

from src.cli.main import main


def test_too_many_input_images(tmp_path: Path, temp_test_images: list[Path]) -> None:
    """Test that more than 3 input images raises validation error."""
    os.environ["GEMINI_API_KEY"] = "test_key"

    # Use all 4 test images (exceeds limit)
    input_paths = ",".join(str(p) for p in temp_test_images)

    exit_code = main(["--prompt", "Test", "--in", input_paths, "--out", str(tmp_path / "out.png")])

    # Verify validation error exit code
    assert exit_code == 2

    # Verify no output file created
    assert not (tmp_path / "out.png").exists()
