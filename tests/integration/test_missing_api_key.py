"""Integration test: missing API key (Scenario 10)."""

import os
from pathlib import Path

from pytest import MonkeyPatch

from src.cli.main import main


def test_missing_api_key(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """Test missing GEMINI_API_KEY error handling.

    Scenario 10: Given GEMINI_API_KEY is not set,
    When they run the CLI tool,
    Then an error message with setup instructions is shown with exit code 1
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    exit_code = main(["--prompt", "Test"])

    assert exit_code == 1  # Configuration error
