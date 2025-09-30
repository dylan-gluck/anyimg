"""CLI argument parser."""

import argparse

from src.models.config import GenerationConfig


def parse_args(args: list[str] | None = None) -> GenerationConfig:
    """Parse CLI arguments into GenerationConfig.

    Args:
        args: Optional list of arguments (defaults to sys.argv)

    Returns:
        GenerationConfig with validated arguments

    Raises:
        Various validation errors from GenerationConfig
    """
    parser = argparse.ArgumentParser(
        prog="anyimg",
        description="Generate images using Google Gemini 2.5 Flash API",
    )

    parser.add_argument(
        "--prompt",
        type=str,
        required=True,
        help="Text prompt for image generation",
    )

    parser.add_argument(
        "--in",
        dest="input_images",
        type=str,
        default=None,
        help="Comma-separated paths to input images (max 3)",
    )

    parser.add_argument(
        "--out",
        dest="output_path",
        type=str,
        default=None,
        help="Output path for generated image (default: anyimg_<timestamp>.png)",
    )

    parser.add_argument(
        "--batch",
        dest="batch_count",
        type=int,
        default=1,
        help="Number of images to generate (default: 1)",
    )

    parsed = parser.parse_args(args)

    # Parse comma-separated input images
    input_image_list = None
    if parsed.input_images:
        input_image_list = [p.strip() for p in parsed.input_images.split(",")]

    # Create and validate config
    return GenerationConfig.from_args(
        prompt=parsed.prompt,
        input_images=input_image_list,
        output_path=parsed.output_path,
        batch_count=parsed.batch_count,
    )
