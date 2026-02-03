"""CLI main entry point."""

import sys
from pathlib import Path
from typing import Sequence

from rich.console import Console

from src.cli.parser import parse_args
from src.models.config import GenerationConfig
from src.models.exceptions import (
    APIError,
    ConfigurationError,
    FileSystemError,
    ValidationError,
)
from src.services.batch_api_service import BatchAPIService
from src.services.batch_service import generate_batch
from src.services.gemini_service import GeminiService
from src.services.image_service import ImageService


def handle_normal_mode(
    config: GenerationConfig,
    console: Console,
    err_console: Console,
) -> int:
    """Handle normal inline generation mode.

    Args:
        config: Generation configuration
        console: Console for output
        err_console: Console for errors

    Returns:
        Exit code (0=success, 3=API error)
    """
    gemini_service = GeminiService()
    image_service = ImageService()

    results = generate_batch(config, gemini_service, image_service)

    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    for result in successful:
        console.print(f"[green]✓[/green] Generated image: {result.output_path}")

    if failed:
        err_console.print(f"\n[yellow]Warning:[/yellow] {len(failed)} generation(s) failed:")
        for result in failed:
            err_console.print(f"  - Index {result.index}: {result.error_message}")

    console.print(f"\n[bold]Summary:[/bold] {len(successful)} successful, {len(failed)} failed")

    return 0 if successful else 3


def handle_batch_api_mode(
    config: GenerationConfig,
    console: Console,
    err_console: Console,
) -> int:
    """Handle batch API mode using JSONL file.

    Args:
        config: Generation configuration (output_path is JSONL file)
        console: Console for output
        err_console: Console for errors

    Returns:
        Exit code (0=success, 1=config, 3=API error)
    """
    jsonl_path = config.output_path

    if jsonl_path is None:
        err_console.print("[red]Error:[/red] Batch file path required for batch API mode")
        return 1

    batch_api = BatchAPIService()

    try:
        console.print(f"[cyan]Creating batch job from {jsonl_path}...[/cyan]")
        job_name = batch_api.create_batch_from_file(jsonl_path)
        console.print(f"[green]✓[/green] Batch job created: {job_name}")
        console.print("[cyan]Polling job status (this may take a while)...[/cyan]")

        final_state = batch_api.poll_batch_status(job_name)

        if final_state == "JOB_STATE_SUCCEEDED":
            console.print("[green]✓[/green] Batch job completed successfully")
            console.print("[cyan]Downloading and processing results...[/cyan]")

            results = batch_api.get_batch_results(job_name)

            output_dir = Path("batch_results")
            saved_paths = batch_api.save_batch_images(results, output_dir)

            console.print(f"\n[green]✓[/green] Saved {len(saved_paths)} images to {output_dir}/")
            for path in saved_paths:
                console.print(f"  - {path}")

            return 0
        else:
            err_console.print(f"[red]Error:[/red] Batch job failed with state: {final_state}")
            return 3

    except APIError as e:
        err_console.print(f"[red]Error:[/red] {e.message}")
        if e.remediation:
            err_console.print(f"[yellow]Fix:[/yellow] {e.remediation}")
        return e.exit_code


def main(args: Sequence[str] | None = None) -> int:
    """Main CLI entry point.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0=success, 1=config, 2=validation, 3=API, 4=filesystem)
    """
    console = Console()
    err_console = Console(stderr=True)

    try:
        config = parse_args(args)

        if config.output_path and str(config.output_path).endswith(".jsonl"):
            return handle_batch_api_mode(config, console, err_console)

        return handle_normal_mode(config, console, err_console)

    except ConfigurationError as e:
        err_console.print(f"[red]Error:[/red] {e.message}")
        if e.remediation:
            err_console.print(f"[yellow]Fix:[/yellow] {e.remediation}")
        return e.exit_code

    except ValidationError as e:
        err_console.print(f"[red]Error:[/red] {e.message}")
        if e.remediation:
            err_console.print(f"[yellow]Fix:[/yellow] {e.remediation}")
        return e.exit_code

    except APIError as e:
        err_console.print(f"[red]Error:[/red] {e.message}")
        if e.remediation:
            err_console.print(f"[yellow]Fix:[/yellow] {e.remediation}")
        return e.exit_code

    except FileSystemError as e:
        err_console.print(f"[red]Error:[/red] {e.message}")
        if e.remediation:
            err_console.print(f"[yellow]Fix:[/yellow] {e.remediation}")
        return e.exit_code

    except ValueError as e:
        # Pydantic validation errors
        err_console.print(f"[red]Validation Error:[/red] {str(e)}")
        return 2

    except Exception as e:
        err_console.print(f"[red]Unexpected error:[/red] {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
