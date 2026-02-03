"""CLI argument parser."""

import argparse
from typing import Sequence

from src.models.config import GenerationConfig


def parse_args(args: Sequence[str] | None = None) -> GenerationConfig:
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

    parser.add_argument(
        "--aspect-ratio",
        type=str,
        default=None,
        choices=["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"],
        help="Aspect ratio for generated image (default: auto)",
    )

    parser.add_argument(
        "--resolution",
        type=str,
        default=None,
        choices=["1K", "2K", "4K"],
        help="Resolution for generated image (default: auto)",
    )

    parser.add_argument(
        "--batch-file",
        type=str,
        default=None,
        help="JSONL file for batch API mode (triggers batch API instead of inline generation)",
    )

    parsed = parser.parse_args(args)

    # Batch mode: use JSONL file directly
    if parsed.batch_file:
        return GenerationConfig.from_args(
            prompt="",
            input_images=[],
            output_path=parsed.batch_file,
            batch_count=1,
            aspect_ratio=parsed.aspect_ratio,
            resolution=parsed.resolution,
        )

    # Normal mode: parse comma-separated input images
    input_image_list = None
    if parsed.input_images:
        input_image_list = [p.strip() for p in parsed.input_images.split(",")]

    # Create and validate config
    return GenerationConfig.from_args(
        prompt=parsed.prompt,
        input_images=input_image_list,
        output_path=parsed.output_path,
        batch_count=parsed.batch_count,
        aspect_ratio=parsed.aspect_ratio,
        resolution=parsed.resolution,
    )
