"""Unit tests for GenerationResult model."""

from datetime import datetime
from pathlib import Path

from src.models.result import GenerationResult


def test_timestamp_auto_generated() -> None:
    """Test: timestamp auto-generated."""
    result = GenerationResult(
        index=0,
        output_path=Path("test.png"),
        success=True,
    )
    assert isinstance(result.timestamp, datetime)
    assert result.timestamp <= datetime.now()


def test_all_fields_stored_correctly() -> None:
    """Test: all fields stored correctly."""
    test_time = datetime(2025, 9, 30, 12, 0, 0)
    result = GenerationResult(
        index=5,
        output_path=Path("/output/image.png"),
        success=False,
        error_message="API timeout",
        timestamp=test_time,
    )

    assert result.index == 5
    assert result.output_path == Path("/output/image.png")
    assert result.success is False
    assert result.error_message == "API timeout"
    assert result.timestamp == test_time
