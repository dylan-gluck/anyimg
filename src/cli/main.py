"""CLI main entry point."""

import sys
from typing import Sequence

from rich.console import Console

from src.cli.parser import parse_args
from src.models.exceptions import (
    APIError,
    ConfigurationError,
    FileSystemError,
    ValidationError,
)
from src.services.batch_service import generate_batch
from src.services.gemini_service import GeminiService
from src.services.image_service import ImageService


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
        # Parse arguments and validate config
        config = parse_args(args)

        # Initialize services
        gemini_service = GeminiService()
        image_service = ImageService()

        # Generate images
        results = generate_batch(config, gemini_service, image_service)

        # Count successes and failures
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        # Print results
        for result in successful:
            console.print(f"[green]✓[/green] Generated image: {result.output_path}")

        if failed:
            err_console.print(f"\n[yellow]Warning:[/yellow] {len(failed)} generation(s) failed:")
            for result in failed:
                err_console.print(f"  - Index {result.index}: {result.error_message}")

        # Print summary
        console.print(f"\n[bold]Summary:[/bold] {len(successful)} successful, {len(failed)} failed")

        # Exit code: 0 if any succeeded
        if successful:
            return 0
        else:
            return 3  # All failed (API error)

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
