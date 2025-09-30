"""Integration test: missing API key (Scenario 10)."""

import subprocess
from pathlib import Path

from pytest import MonkeyPatch


def test_missing_api_key(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """Test missing GEMINI_API_KEY error handling.

    Scenario 10: Given GEMINI_API_KEY is not set,
    When they run the CLI tool,
    Then an error message with setup instructions is shown with exit code 1
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    result = subprocess.run(
        ["uv", "run", "python", "-m", "src", "--prompt", "Test"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1  # Configuration error
    assert "GEMINI_API_KEY" in result.stderr
    assert "export" in result.stderr.lower() or "set" in result.stderr.lower()
