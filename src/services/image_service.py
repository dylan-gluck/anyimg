"""Image I/O service for loading and saving images."""

from pathlib import Path

from PIL import Image

from src.models.exceptions import DirectoryCreationError, FileSystemError


class ImageService:
    """Service for image file operations."""

    @staticmethod
    def load_input_images(paths: list[Path]) -> list[Image.Image]:
        """Load input images from file paths.

        Args:
            paths: List of image file paths

        Returns:
            List of PIL Image objects

        Raises:
            FileSystemError: If image cannot be loaded
        """
        images = []
        for path in paths:
            try:
                img = Image.open(path)
                images.append(img)
            except Exception as e:
                raise FileSystemError(
                    f"Failed to load image: {path}",
                    remediation=f"Ensure {path} is a valid image file",
                ) from e
        return images

    @staticmethod
    def save_image(image_data: bytes, output_path: Path) -> None:
        """Save image data to file.

        Args:
            image_data: Raw image bytes
            output_path: Where to save the image

        Raises:
            DirectoryCreationError: If output directory cannot be created
            FileSystemError: If image cannot be saved
        """
        try:
            # Create parent directory if needed
            if output_path.parent != Path("."):
                output_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise DirectoryCreationError(
                f"Failed to create directory: {output_path.parent}",
                remediation="Check directory permissions",
            ) from e

        try:
            # Write image data
            output_path.write_bytes(image_data)
        except Exception as e:
            raise FileSystemError(
                f"Failed to save image: {output_path}",
                remediation="Check file permissions and disk space",
            ) from e
