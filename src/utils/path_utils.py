"""Path utility functions for file handling."""

from datetime import datetime
from pathlib import Path

from src.models.exceptions import InvalidInputImageError


def validate_input_image(path: Path) -> None:
    """Validate input image exists and has valid format.

    Args:
        path: Path to input image

    Raises:
        InvalidInputImageError: If image doesn't exist or has invalid format
    """
    if not path.exists():
        raise InvalidInputImageError(
            f"Input image not found: {path}",
            remediation=f"Ensure file exists: {path}",
        )

    if not path.is_file():
        raise InvalidInputImageError(
            f"Input image is not a file: {path}",
            remediation=f"Provide a file path, not a directory: {path}",
        )

    valid_formats = {".png", ".jpg", ".jpeg"}
    if path.suffix.lower() not in valid_formats:
        raise InvalidInputImageError(
            f"Invalid input image format: {path}. Only PNG and JPEG/JPG are supported.",
            remediation="Provide PNG or JPEG/JPG images only",
        )


def generate_timestamp_filename() -> str:
    """Generate timestamped filename.

    Returns:
        Filename in format "anyimg_YYYYMMDD_HHMMSS.png"
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"anyimg_{timestamp}.png"


def resolve_output_path(path: Path | None) -> Path:
    """Resolve output path, handling default naming.

    Args:
        path: Custom output path or None for default

    Returns:
        Resolved output path
    """
    if path is None:
        return Path(generate_timestamp_filename())
    return path


def auto_rename_if_exists(path: Path) -> Path:
    """Auto-rename path with suffix if it exists.

    Args:
        path: Desired output path

    Returns:
        Available path (original or with _1, _2, etc. suffix)
    """
    if not path.exists():
        return path

    # Path exists, find available suffix
    stem = path.stem
    suffix = path.suffix
    parent = path.parent

    counter = 1
    while True:
        new_path = parent / f"{stem}_{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1
