# Research: Gemini 2.5 Flash Image Generation CLI

**Feature**: 001-we-are-building
**Date**: 2025-09-30
**Status**: Complete

## Research Questions

### 1. Google Gemini 2.5 Flash API for Image Generation

**Decision**: Use `google.genai` Python SDK with the `gemini-2.5-flash-image-preview` model

**Rationale**:
- Official Google SDK (`google-genai` package, not `google-generativeai`)
- `gemini-2.5-flash-image-preview` model supports direct image generation
- Supports multimodal input (text + images) for context-aware generation
- Simple client-based API pattern
- Response includes image data as bytes for direct file writing

**Implementation Details** (based on demo project /home/d/workspace/projects/logo-designer):
- Install package: `google-genai`
- API key via environment variable (auto-detected by SDK)
- Initialize: `client = genai.Client()`
- Generate image:
  ```python
  response = client.models.generate_content(
      model="gemini-2.5-flash-image-preview",
      contents=prompt,  # Can also include PIL Image objects for multimodal
  )
  ```
- Extract image from response:
  ```python
  image_parts = [
      part.inline_data.data
      for part in response.candidates[0].content.parts
      if part.inline_data
  ]
  generated_image = Image.open(BytesIO(image_parts[0]))
  generated_image.save(output_path)
  ```

**Alternatives Considered**:
- `google-generativeai` package: Rejected - older SDK, demo uses `google-genai`
- Direct REST API calls: Rejected - more boilerplate, manual retry logic
- LangChain Gemini wrapper: Rejected - unnecessary abstraction for CLI tool

**References**:
- https://ai.google.dev/gemini-api/docs/image-generation
- Demo project: /home/d/workspace/projects/logo-designer/main.py

---

### 2. UV for Python Dependency Management

**Decision**: Use UV 0.4+ as package manager and virtual environment tool

**Rationale**:
- 10-100x faster than pip for dependency resolution
- Built-in virtual environment management (`uv venv`, `uv pip install`)
- Compatible with `pyproject.toml` standard (PEP 517/621)
- Lockfile support for reproducible builds
- Drop-in replacement for pip commands

**Implementation Details**:
- Initialize project: `uv init`
- Add dependencies: `uv add google-genai rich pydantic pillow`
- Dev dependencies: `uv add --dev pytest pytest-mock pyright ruff`
- Run commands: `uv run python -m src.cli.main`
- Lock dependencies: `uv.lock` file auto-generated

**Alternatives Considered**:
- Poetry: Rejected - slower, more complex configuration
- pip + venv: Rejected - no lockfile, slow resolution
- Pipenv: Rejected - maintenance concerns, slower than UV

**References**:
- https://github.com/astral-sh/uv
- https://docs.astral.sh/uv/

---

### 3. Rich Library for CLI Output Styling

**Decision**: Use Rich 13+ for terminal output formatting

**Rationale**:
- Provides styled console output (colors, bold, italic)
- Progress bars for batch operations
- Automatic fallback for non-TTY environments
- Writes to stdout/stderr appropriately
- Minimal API for simple use cases

**Implementation Details**:
- Use `rich.console.Console()` for output
- Error messages via `console.print("[red]Error:[/red] message", file=sys.stderr)`
- Success messages via `console.print("[green]✓[/green] Generated image: path")`
- Progress tracking: `rich.progress.track()` for batch loops
- Console object shared via dependency injection

**Alternatives Considered**:
- click.echo with colors: Rejected - less feature-rich, manual styling
- colorama: Rejected - lower-level, no structured output
- Plain print(): Rejected - no styling, constitution requires clear output

**References**:
- https://rich.readthedocs.io/en/stable/console.html
- https://rich.readthedocs.io/en/stable/progress.html

---

### 4. Pydantic for Type Validation

**Decision**: Use Pydantic 2.x for all data models and validation

**Rationale**:
- Runtime validation of CLI arguments and API responses
- Type-safe configuration objects
- Automatic conversion (str → Path, str → int)
- Clear validation error messages
- Integrates with pyright for static type checking

**Implementation Details**:
- Create `GenerationConfig` model for CLI args validation
- Create `ImageGenerationRequest` model for API request structure
- Use `Field()` for validation rules (min/max values, regex patterns)
- Use `@field_validator` for custom validation (file existence, format checks)
- Use `.model_dump()` for serialization

**Alternatives Considered**:
- dataclasses + manual validation: Rejected - no runtime validation
- attrs: Rejected - less feature-rich than Pydantic
- TypedDict: Rejected - no runtime validation

**References**:
- https://docs.pydantic.dev/latest/
- https://docs.pydantic.dev/latest/concepts/models/

---

### 5. Testing Strategy with Pytest, Pyright, Ruff

**Decision**: Use pytest for testing, pyright for type checking, ruff for linting

**Rationale**:
- **pytest**: De facto standard for Python testing, rich plugin ecosystem
- **pyright**: Fast, accurate type checker (used by VS Code Pylance)
- **ruff**: 10-100x faster than flake8/black, combines linting + formatting

**Implementation Details**:
- **pytest**:
  - Use `pytest-mock` for mocking Gemini API calls
  - Use `pytest-asyncio` if async operations added later
  - Store contract tests in `tests/contract/test_gemini_api.py`
  - Use fixtures for temporary directories and mock API responses
- **pyright**:
  - Config in `pyproject.toml`: `typeCheckingMode = "strict"`
  - Run via `uv run pyright src/ tests/`
- **ruff**:
  - Config in `pyproject.toml`: enable `E`, `F`, `I` rule sets
  - Run linting: `uv run ruff check src/ tests/`
  - Run formatting: `uv run ruff format src/ tests/`

**Alternatives Considered**:
- unittest: Rejected - more verbose than pytest
- mypy: Rejected - pyright is faster and more accurate
- black + flake8: Rejected - ruff combines both, much faster

**References**:
- https://docs.pytest.org/
- https://microsoft.github.io/pyright/
- https://docs.astral.sh/ruff/

---

### 6. File I/O and Path Validation

**Decision**: Use `pathlib.Path` for all file operations

**Rationale**:
- Object-oriented path manipulation (vs string concatenation)
- Cross-platform path handling (Windows vs Unix)
- Built-in validation methods (`.exists()`, `.is_file()`, `.suffix`)
- Type-safe with Pydantic (Pydantic supports Path types natively)

**Implementation Details**:
- Accept CLI args as strings, convert to Path in Pydantic model
- Validate input images: `path.exists() and path.is_file() and path.suffix in ['.png', '.jpg', '.jpeg']`
- Create output directories: `output_path.parent.mkdir(parents=True, exist_ok=True)`
- Auto-rename on collision: Check `path.exists()`, append `_1`, `_2`, etc.
- Generate timestamps: `datetime.now().strftime('%Y%m%d_%H%M%S')`

**Alternatives Considered**:
- `os.path` module: Rejected - string-based, less readable
- Manual string manipulation: Rejected - error-prone, not cross-platform

**References**:
- https://docs.python.org/3/library/pathlib.html

---

### 7. Gemini API Image Input Handling

**Decision**: Use `PIL.Image.open()` to read input images, pass to Gemini as PIL Image objects

**Rationale**:
- google-generativeai SDK accepts PIL Image objects directly
- PIL handles format detection and validation automatically
- Allows pre-processing if needed (resize, format conversion)
- Part of Pillow library (de facto standard for image processing)

**Implementation Details**:
- Read input images: `Image.open(path)` for each input path
- Validate format in exception handler (IOError → invalid format)
- Pass to Gemini: `model.generate_content([prompt, img1, img2, img3])`
- No need to manually encode to base64 (SDK handles it)

**Alternatives Considered**:
- Read as bytes, manual base64 encoding: Rejected - SDK handles this
- Direct file path strings: Rejected - less control over validation

**References**:
- https://pillow.readthedocs.io/
- https://ai.google.dev/gemini-api/docs/vision

---

### 8. Error Handling Strategy

**Decision**: Custom exception hierarchy with user-friendly messages

**Rationale**:
- Constitution requires clear error messages with remediation steps
- Distinguish between user errors (invalid input) vs system errors (API failure)
- Enable appropriate exit codes per error type

**Implementation Details**:
- Define exceptions:
  - `ConfigurationError` (exit 1): Missing API key, invalid config
  - `ValidationError` (exit 2): Invalid input files, bad parameters
  - `APIError` (exit 3): Gemini API failures, timeouts
  - `FileSystemError` (exit 4): Cannot write output, permission denied
- Catch exceptions at CLI entry point
- Print error to stderr with remediation: `console.print(f"[red]Error:[/red] {msg}\n[yellow]Fix:[/yellow] {fix}", file=sys.stderr)`
- Example: "GEMINI_API_KEY not found. Set it with: export GEMINI_API_KEY=your_key"

**Alternatives Considered**:
- Generic exceptions: Rejected - no meaningful exit codes
- Stack traces to users: Rejected - violates constitution (clear errors)

---

## Resolution of Spec Ambiguities

### FR-012: What specific error conditions should show messages?

**Resolution**: All error conditions require clear messages with remediation:
1. **File errors**: "Input image not found: /path/to/image.png"
2. **API errors**: "Gemini API request failed: {reason}. Check your internet connection."
3. **Network issues**: "Request timed out after 60 seconds. Retry or check network."
4. **Invalid parameters**: "Batch count must be positive, got: -5"
5. **Missing config**: "GEMINI_API_KEY not found. Set it with: export GEMINI_API_KEY=key"

### FR-018: Should there be rate limiting between batch requests?

**Resolution**: No explicit rate limiting between batch requests. Rationale:
- Gemini API has server-side rate limiting that returns appropriate errors
- Users can control batch size via `--batch` parameter
- Adding artificial delays would frustrate users unnecessarily
- If API rate limit hit: Continue processing, report failures at end (per FR-019)
- Future enhancement: Add `--delay` flag if users request it

---

## Summary

All technical unknowns resolved. Ready for Phase 1 (Design & Contracts).

**Key Decisions**:
1. google-generativeai SDK for API access
2. UV for dependency management
3. Rich for CLI output styling
4. Pydantic for type validation
5. pytest + pyright + ruff for testing
6. pathlib.Path for file operations
7. PIL for image input handling
8. Custom exception hierarchy for error handling

**No blocking uncertainties remain.**