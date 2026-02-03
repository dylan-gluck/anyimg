"""Batch API service for handling JSONL-based batch image generation jobs."""

import base64
import json
import time
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types

from src.models.exceptions import APIError, ConfigurationError


class BatchAPIError(APIError):
    """Error for batch API operations."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            remediation="Check batch job status and try again",
        )


class BatchAPIService:
    """Service for batch image generation via Gemini Batch API."""

    # Completed job states
    COMPLETED_STATES = {
        "JOB_STATE_SUCCEEDED",
        "JOB_STATE_FAILED",
        "JOB_STATE_CANCELLED",
        "JOB_STATE_EXPIRED",
    }

    def __init__(self, client: genai.Client | None = None) -> None:
        """Initialize Batch API service.

        Args:
            client: Optional genai.Client instance for testing. If None, creates new client.
        """
        self.client = client if client is not None else genai.Client()

    def create_batch_from_file(
        self,
        jsonl_path: Path,
        display_name: str | None = None,
    ) -> str:
        """Create batch job from JSONL file.

        Args:
            jsonl_path: Path to JSONL file with batch requests
            display_name: Optional display name for batch job

        Returns:
            Batch job name

        Raises:
            ConfigurationError: If file upload fails
            APIError: If batch job creation fails
        """
        try:
            uploaded_file = self.client.files.upload(
                file=str(jsonl_path),
                config=types.UploadFileConfig(
                    display_name=display_name or jsonl_path.name,
                    mime_type="jsonl",
                ),
            )

            batch_job = self.client.batches.create(
                model="gemini-3-pro-image-preview",
                src=uploaded_file.name,  # type: ignore[arg-type]
                config={
                    "display_name": display_name or f"batch-{jsonl_path.name}",
                },
            )

            if batch_job is None:  # type: ignore[comparison-overlap]
                raise BatchAPIError("Batch job creation returned None")

            return batch_job.name  # type: ignore[return-value]

        except Exception as e:
            error_msg = str(e).lower()

            if "401" in error_msg or "unauthorized" in error_msg or "auth" in error_msg:
                raise ConfigurationError(
                    message="Authentication failed",
                    remediation="Check your GEMINI_API_KEY environment variable",
                ) from e
            else:
                raise APIError(
                    message=f"Failed to create batch job: {str(e)}",
                    remediation="Check your JSONL file format and retry",
                ) from e

    def poll_batch_status(
        self,
        job_name: str,
        poll_interval: int = 10,
        timeout: int | None = None,
    ) -> str:
        """Poll batch job status until completion.

        Args:
            job_name: Batch job name
            poll_interval: Seconds between status checks
            timeout: Maximum seconds to wait (None for no timeout)

        Returns:
            Final job state

        Raises:
            BatchAPIError: If job fails or times out
        """
        start_time = time.time()

        while True:
            batch_job = self.client.batches.get(name=job_name)
            state = batch_job.state.name  # type: ignore[union-attr]

            # Check if completed
            if state in self.COMPLETED_STATES:
                return state

            # Check timeout
            if timeout and (time.time() - start_time) > timeout:
                raise BatchAPIError(
                    f"Batch job timed out after {timeout} seconds. Current state: {state}",
                )

            # Wait before next poll
            time.sleep(poll_interval)

    def get_batch_results(
        self,
        job_name: str,
    ) -> list[dict[str, Any]]:
        """Download and parse batch job results.

        Args:
            job_name: Batch job name

        Returns:
            List of result dictionaries (one per request)

        Raises:
            BatchAPIError: If job did not succeed or results parsing fails
        """
        try:
            batch_job = self.client.batches.get(name=job_name)
            state = batch_job.state.name  # type: ignore[union-attr]

            if state != "JOB_STATE_SUCCEEDED":
                raise BatchAPIError(
                    f"Batch job did not succeed. State: {state}, Error: {batch_job.error}",  # type: ignore[union-attr]
                )

            result_file_name = batch_job.dest.file_name  # type: ignore[union-attr]
            file_content_bytes = self.client.files.download(file=result_file_name)  # type: ignore[arg-type]
            file_content = file_content_bytes.decode("utf-8")

            # Parse JSONL results
            results = []
            for line in file_content.splitlines():
                if line:
                    parsed_response = json.loads(line)
                    results.append(parsed_response)

            return results

        except BatchAPIError:
            raise
        except Exception as e:
            raise BatchAPIError(
                f"Failed to get batch results: {str(e)}",
            ) from e

    def save_batch_images(
        self,
        results: list[dict[str, Any]],
        output_dir: Path,
    ) -> list[str]:
        """Save images from batch results to files.

        Args:
            results: Parsed batch results
            output_dir: Directory to save images

        Returns:
            List of saved file paths

        Raises:
            BatchAPIError: If image saving fails
        """
        saved_paths: list[str] = []  # type: ignore[assignment]

        try:
            output_dir.mkdir(parents=True, exist_ok=True)

            for i, result in enumerate(results, start=1):
                key = result.get("key", f"request-{i}")

                # Check for error
                if "error" in result:
                    print(f"[yellow]Warning:[/yellow] Request {key} failed: {result['error']}")
                    continue

                # Extract and save image
                if "response" in result and result["response"]:
                    candidates = result["response"].get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])

                        for part in parts:
                            if "inlineData" in part:
                                mime_type = part["inlineData"].get("mimeType", "image/png")
                                data = base64.b64decode(part["inlineData"]["data"])

                                # Determine file extension
                                ext = ".png" if "png" in mime_type else ".jpg"

                                file_path = output_dir / f"{key}{ext}"
                                with open(file_path, "wb") as f:
                                    f.write(data)

                                saved_paths.append(str(file_path))  # type: ignore[arg-type]

            return saved_paths

        except Exception as e:
            raise BatchAPIError(
                f"Failed to save batch images: {str(e)}",
            ) from e
