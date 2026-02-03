"""Batch generation orchestrator for handling multiple image generations."""

from src.models.config import GenerationConfig
from src.models.request import ImageGenerationRequest
from src.models.result import GenerationResult
from src.services.gemini_service import GeminiService
from src.services.image_service import ImageService
from src.utils.path_utils import auto_rename_if_exists, resolve_output_path


def generate_batch(
    config: GenerationConfig,
    gemini_service: GeminiService,
    image_service: ImageService,
) -> list[GenerationResult]:
    """Generate batch of images.

    Args:
        config: Generation configuration
        gemini_service: Service for API calls
        image_service: Service for file I/O

    Returns:
        List of GenerationResult for each attempt (both success and failure)
    """
    results: list[GenerationResult] = []

    # Load input images once (if any)
    input_pil_images = (
        image_service.load_input_images(config.input_images) if config.input_images else []
    )

    for i in range(config.batch_count):
        # Generate output path
        if config.output_path:
            # Custom path: add index for batch mode
            if config.batch_count > 1:
                stem = config.output_path.stem
                suffix = config.output_path.suffix
                parent = config.output_path.parent
                output_path = parent / f"{stem}_{i + 1}{suffix}"
            else:
                output_path = config.output_path
        else:
            # Default timestamped path
            output_path = resolve_output_path(None)

        # Auto-rename if exists
        output_path = auto_rename_if_exists(output_path)

        try:
            # Create request
            request = ImageGenerationRequest(
                prompt=config.prompt,
                input_images=input_pil_images,
                aspect_ratio=config.aspect_ratio,
                resolution=config.resolution,
            )

            # Generate image
            response = gemini_service.generate_image(request)

            if response.success:
                # Save image
                image_service.save_image(response.image_data, output_path)

                # Record success
                results.append(
                    GenerationResult(
                        index=i,
                        output_path=output_path,
                        success=True,
                        error_message=None,
                    )
                )
            else:
                # Record API failure
                results.append(
                    GenerationResult(
                        index=i,
                        output_path=output_path,
                        success=False,
                        error_message=response.error_message,
                    )
                )

        except Exception as e:
            # Record exception
            results.append(
                GenerationResult(
                    index=i,
                    output_path=output_path,
                    success=False,
                    error_message=str(e),
                )
            )
            # Continue with next iteration (don't abort batch)

    return results
