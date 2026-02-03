# AGENTS.md

## Project Overview

CLI for generating images using Google Gemini 2.5 Flash API (aka Nano Banana).
Python 3.11+ project managed with UV.

---

## Build & Test Commands

**Installation (local development):**
```bash
uv sync
```

**Run all tests:**
```bash
uv run pytest -v
```

**Run single test:**
```bash
uv run pytest tests/unit/test_config.py::test_prompt_validation_non_empty -v
```

**Run test categories:**
```bash
# Unit tests only
uv run pytest tests/unit/ -v

# Integration tests only
GEMINI_API_KEY="test_key" uv run pytest tests/integration/ -v

# Contract tests (mocked API)
uv run pytest tests/contract/ -v
```

**Type checking:**
```bash
uv run pyright src/ tests/
```

**Linting:**
```bash
uv run ruff check src/ tests/
```

**Formatting:**
```bash
uv run ruff format src/ tests/
```

---

## Code Style Guidelines

### Formatting & Linting
- **Line length**: 100 characters (enforced by ruff)
- **Quote style**: Double quotes for strings
- **Indentation**: 4 spaces
- **Type checking**: Pyright strict mode
- **Python version**: 3.11+ (type annotations use `|` union syntax)

### Imports
- Standard Python import ordering (stdlib, third-party, local)
- No isort configuration - organize manually
- Use absolute imports from `src` package:
  ```python
  from src.models.config import GenerationConfig
  from src.services.gemini_service import GeminiService
  ```

### Type Annotations
- **Mandatory** for all function parameters and return values
- Use `|` union syntax (not `Union` from typing):
  ```python
  def parse_args(args: Sequence[str] | None = None) -> GenerationConfig:
      pass
  ```
- Use `list[T]`, `dict[K, V]` syntax (not `List`, `Dict` from typing)

### Naming Conventions
- **Functions/variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE` (though rarely used)
- **Private members**: `_underscore_prefix`

### Docstrings
- Google-style docstrings on all public functions/classes
- Include Args, Returns, Raises sections where applicable:
  ```python
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
          List of GenerationResult for each attempt
      """
  ```

### Error Handling
- **Custom exception hierarchy** (exit codes documented in CLI):
  - `ConfigurationError` (exit code 1): API key issues, auth failures
  - `ValidationError` (exit code 2): Invalid inputs, format issues
  - `APIError` (exit code 3): Timeouts, rate limits, API failures
  - `FileSystemError` (exit code 4): File permissions, directory creation

- **Always include remediation messages** for user-facing errors:
  ```python
  raise ConfigurationError(
      message="Authentication failed",
      remediation="Check your GEMINI_API_KEY environment variable",
  )
  ```

- **Never catch bare `Exception`** - catch specific exceptions
- Use `try/except` blocks with specific exception types

### Pydantic Models
- All config/data models use Pydantic `BaseModel`
- Use `Field()` for validation rules and descriptions
- Use `@field_validator` for custom validation logic:
  ```python
  @field_validator("prompt")
  @classmethod
  def validate_prompt(cls, v: str) -> str:
      v = v.strip()
      if not v:
          raise ValueError("Prompt cannot be empty")
      return v
  ```

### Dependency Injection
- Services accept optional client dependencies for testing:
  ```python
  def __init__(self, client: genai.Client | None = None) -> None:
      self.client = client if client is not None else genai.Client()
  ```

---

## Project Structure

```
src/
├── cli/          # CLI entry point (main.py, parser.py)
├── models/       # Pydantic models (config, request, response, exceptions.py)
├── services/     # Core logic (gemini_service, image_service, batch_service)
└── utils/        # Helper functions (path_utils)
tests/
├── unit/        # Unit tests for models
├── integration/ # End-to-end workflow tests
└── contract/    # API contract tests (mocked)
```

---

## Testing Patterns

**Test file naming:** `test_*.py` matching the module under test

**Fixtures:**
- `tmp_path` for temporary files
- `monkeypatch` for environment variables
- Custom fixtures in `conftest.py` (mocks, sample data)

**Test organization:**
- Unit tests: test individual functions/models
- Integration tests: test full CLI workflows
- Contract tests: verify API contract with mocks

**Test naming:** Descriptive docstrings with scenario description:
```python
def test_prompt_validation_non_empty() -> None:
    """Test: prompt validation (non-empty, stripped)."""
    pass
```

**Mock external dependencies:** Always mock `genai.Client` in tests
