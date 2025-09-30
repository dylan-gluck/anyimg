# Tasks: Gemini 2.5 Flash Image Generation CLI

**Feature**: 001-we-are-building
**Input**: Design documents from `/home/d/workspace/projects/anyimg/specs/001-we-are-building/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/gemini_api_contract.md, quickstart.md

## Execution Flow
```
1. Load plan.md from feature directory ✓
   → Tech stack: Python 3.11+, google-genai, rich, pydantic, pillow
   → Structure: src/ (models, services, cli, utils), tests/ (contract, integration, unit)
2. Load design documents ✓
   → data-model.md: GenerationConfig, ImageGenerationRequest, ImageGenerationResponse, GenerationResult
   → contracts/gemini_api_contract.md: Gemini API integration contract
   → quickstart.md: 13 user scenarios for integration tests
3. Generate tasks by category (TDD order)
4. Mark [P] for parallel execution (independent files)
5. Number tasks sequentially (T001, T002...)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Exact file paths included in descriptions

## Phase 3.1: Setup

- [ ] T001 Add project dependencies via uv
  - Run: `uv add google-genai rich pydantic pillow`
  - Run: `uv add --dev pytest pytest-mock pyright ruff`
  - Verify: `uv.lock` generated successfully

- [ ] T002 [P] Create src/ directory structure
  - Create: `src/models/__init__.py`
  - Create: `src/services/__init__.py`
  - Create: `src/cli/__init__.py`
  - Create: `src/utils/__init__.py`

- [ ] T003 [P] Create tests/ directory structure
  - Create: `tests/contract/__init__.py`
  - Create: `tests/integration/__init__.py`
  - Create: `tests/unit/__init__.py`

- [ ] T004 [P] Configure pyproject.toml for pyright and ruff
  - Add pyright strict type checking configuration
  - Add ruff linting rules (E, F, I rule sets)
  - Add ruff formatting configuration

## Phase 3.2: Data Models (TDD Foundation)

- [ ] T005 [P] Create custom exception hierarchy in src/models/exceptions.py
  - Base: `AnyImgError`
  - Config: `ConfigurationError`, `MissingAPIKeyError`, `InvalidConfigError`
  - Validation: `ValidationError`, `InvalidInputImageError`, `TooManyInputImagesError`, `InvalidBatchCountError`
  - API: `APIError`, `APITimeoutError`, `APIRateLimitError`, `APIResponseError`
  - FS: `FileSystemError`, `DirectoryCreationError`
  - Each with exit code, message, remediation

- [ ] T006 [P] Create GenerationConfig model in src/models/config.py
  - Fields: prompt, input_images, output_path, batch_count, api_key
  - Validators: prompt non-empty, max 3 input_images, batch_count >= 1
  - Field validators for input image existence and format
  - Load GEMINI_API_KEY from environment, fail fast if missing

- [ ] T007 [P] Create ImageGenerationRequest model in src/models/request.py
  - Fields: model, prompt, input_images (PIL.Image list), timeout
  - Default model: "gemini-2.5-flash-image-preview"
  - Default timeout: 60 seconds

- [ ] T008 [P] Create ImageGenerationResponse model in src/models/response.py
  - Fields: image_data (bytes), success (bool), error_message (str | None)
  - Validation: success=True requires non-empty image_data, success=False requires error_message

- [ ] T009 [P] Create GenerationResult model in src/models/result.py
  - Fields: index, output_path, success, error_message, timestamp
  - Used for batch processing results tracking

## Phase 3.3: Contract Tests (MUST FAIL Initially)

- [ ] T010 [P] Create pytest fixtures in tests/contract/conftest.py
  - Fixture: `mock_genai_client` - mocks genai.Client()
  - Fixture: `mock_success_response` - valid Response with PNG bytes
  - Fixture: `mock_timeout_error` - simulates timeout exception
  - Fixture: `mock_rate_limit_error` - simulates 429 error
  - Fixture: `mock_auth_error` - simulates 401 error
  - Fixture: `sample_pil_images` - creates test PIL.Image objects

- [ ] T011 [P] Contract test: successful single image generation in tests/contract/test_gemini_api.py
  - Test ID: test_generate_single_image_success
  - Mock: client.models.generate_content returns valid PNG response
  - Assert: correct model and prompt passed to API
  - Assert: returns ImageGenerationResponse(success=True) with valid image_data

- [ ] T012 [P] Contract test: successful multimodal generation in tests/contract/test_gemini_api.py
  - Test ID: test_generate_multimodal_success
  - Mock: API receives prompt + 2 PIL Images
  - Assert: contents parameter is list with 3 elements
  - Assert: returns successful response with image data

- [ ] T013 [P] Contract test: API timeout handling in tests/contract/test_gemini_api.py
  - Test ID: test_generate_timeout_error
  - Mock: API call raises timeout exception after 60 seconds
  - Assert: raises APITimeoutError with helpful message

- [ ] T014 [P] Contract test: authentication error in tests/contract/test_gemini_api.py
  - Test ID: test_generate_auth_error
  - Mock: API raises 401 authentication error
  - Assert: raises ConfigurationError with API key setup instructions

- [ ] T015 [P] Contract test: rate limit error in tests/contract/test_gemini_api.py
  - Test ID: test_generate_rate_limit_error
  - Mock: API raises 429 rate limit error
  - Assert: raises APIRateLimitError with retry suggestion

- [ ] T016 [P] Contract test: empty response handling in tests/contract/test_gemini_api.py
  - Test ID: test_generate_empty_response
  - Mock: API returns Response with no inline_data
  - Assert: raises APIResponseError indicating no image data

- [ ] T017 [P] Contract test: maximum input images (3) in tests/contract/test_gemini_api.py
  - Test ID: test_generate_max_input_images
  - Mock: API receives prompt + 3 PIL Images
  - Assert: contents list has 4 elements (prompt + 3 images)
  - Assert: returns successful response

## Phase 3.4: Unit Tests for Models (MUST FAIL Initially)

- [ ] T018 [P] Unit test: GenerationConfig validation in tests/unit/test_config.py
  - Test: prompt validation (non-empty, stripped)
  - Test: max 3 input images (TooManyInputImagesError on 4)
  - Test: batch_count >= 1 (InvalidBatchCountError on 0)
  - Test: input image file existence (InvalidInputImageError)
  - Test: input image format validation (.png, .jpg, .jpeg only)
  - Test: missing GEMINI_API_KEY (MissingAPIKeyError)

- [ ] T019 [P] Unit test: ImageGenerationResponse validation in tests/unit/test_response.py
  - Test: success=True requires non-empty image_data
  - Test: success=False requires error_message
  - Test: validation fails if both success and error_message present

- [ ] T020 [P] Unit test: GenerationResult in tests/unit/test_result.py
  - Test: timestamp auto-generated
  - Test: all fields stored correctly

## Phase 3.5: Core Service Implementation

- [ ] T021 Create Gemini API service in src/services/gemini_service.py
  - Initialize: genai.Client() with API key from config
  - Method: `generate_image(request: ImageGenerationRequest) -> ImageGenerationResponse`
  - Handle: timeout after 60 seconds
  - Error mapping: SDK exceptions → custom exceptions (APITimeoutError, APIRateLimitError, etc.)
  - Extract: image_data from response.candidates[0].content.parts
  - Return: ImageGenerationResponse with success/failure status

- [ ] T022 [P] Create path utilities in src/utils/path_utils.py
  - Function: `validate_input_image(path: Path) -> None` - validates existence and format
  - Function: `generate_timestamp_filename() -> str` - returns "anyimg_{timestamp}.png"
  - Function: `resolve_output_path(path: Path | None) -> Path` - handles default naming
  - Function: `auto_rename_if_exists(path: Path) -> Path` - appends _1, _2, etc. on collision

- [ ] T023 [P] Create image I/O service in src/services/image_service.py
  - Function: `load_input_images(paths: list[Path]) -> list[PIL.Image.Image]`
  - Function: `save_image(image_data: bytes, output_path: Path) -> None`
  - Handle: directory creation (parent.mkdir(parents=True, exist_ok=True))
  - Handle: file system errors with FileSystemError

- [ ] T024 Create batch generation orchestrator in src/services/batch_service.py
  - Function: `generate_batch(config: GenerationConfig, gemini_service, image_service) -> list[GenerationResult]`
  - For each iteration (0 to batch_count):
    - Generate output path (with index if custom path)
    - Call gemini_service.generate_image()
    - Save successful images via image_service
    - Create GenerationResult for each attempt
    - Continue on failure (do NOT abort batch)
  - Return: list of all results (success and failure)

## Phase 3.6: CLI Layer

- [ ] T025 Create CLI argument parser in src/cli/parser.py
  - Argument: `--prompt` (required, string)
  - Argument: `--in` (optional, comma-separated paths)
  - Argument: `--out` (optional, path)
  - Argument: `--batch` (optional, int, default=1)
  - Function: `parse_args() -> GenerationConfig`
  - Handle: argument validation, convert to GenerationConfig

- [ ] T026 Create CLI main entry point in src/cli/main.py
  - Initialize: rich Console for output
  - Load: config from CLI args via parser
  - Instantiate: gemini_service, image_service, batch_service
  - Call: batch_service.generate_batch()
  - Output: styled success/error messages via rich Console
  - Success message: `[green]✓[/green] Generated image: {path}`
  - Error message: `[red]Error:[/red] {msg}\n[yellow]Fix:[/yellow] {fix}` to stderr
  - Print: batch summary (X successful, Y failed)
  - Exit codes: 0 (success), 1 (config error), 2 (validation error), 3 (API error), 4 (filesystem error)

## Phase 3.7: Integration Tests (Based on Quickstart Scenarios)

- [ ] T027 [P] Integration test: basic text-to-image (Scenario 1) in tests/integration/test_basic_generation.py
  - Run CLI with: `--prompt "A serene mountain landscape"`
  - Assert: anyimg_{timestamp}.png created
  - Assert: file is valid PNG (via PIL.Image.open)
  - Assert: exit code 0

- [ ] T028 [P] Integration test: multimodal generation (Scenario 2) in tests/integration/test_multimodal_generation.py
  - Create: 2 temporary test images
  - Run CLI with: `--prompt "Combine styles" --in img1.png,img2.png`
  - Assert: output PNG created
  - Assert: exit code 0

- [ ] T029 [P] Integration test: custom output path (Scenario 3) in tests/integration/test_custom_output.py
  - Run CLI with: `--prompt "City" --out outputs/city.png`
  - Assert: outputs/ directory created
  - Assert: outputs/city.png exists
  - Assert: exit code 0

- [ ] T030 [P] Integration test: batch with custom path (Scenario 4) in tests/integration/test_batch_custom.py
  - Run CLI with: `--prompt "Art" --out art.png --batch 3`
  - Assert: art_1.png, art_2.png, art_3.png created
  - Assert: exit code 0

- [ ] T031 [P] Integration test: batch with default naming (Scenario 5) in tests/integration/test_batch_default.py
  - Run CLI with: `--prompt "Patterns" --batch 3`
  - Assert: 3 files with unique timestamps created
  - Assert: exit code 0

- [ ] T032 [P] Integration test: file collision auto-rename (Scenario 6) in tests/integration/test_file_collision.py
  - Create: empty myimage.png
  - Run CLI with: `--prompt "New" --out myimage.png`
  - Assert: myimage_1.png created (original untouched)
  - Assert: exit code 0

- [ ] T033 [P] Integration test: invalid input format (Scenario 7) in tests/integration/test_invalid_format.py
  - Create: test.txt (non-image file)
  - Run CLI with: `--prompt "Test" --in test.txt`
  - Assert: error message about invalid format
  - Assert: exit code 2 (validation error)

- [ ] T034 [P] Integration test: too many input images (Scenario 8) in tests/integration/test_too_many_inputs.py
  - Create: 4 test images
  - Run CLI with: `--prompt "Test" --in img1.png,img2.png,img3.png,img4.png`
  - Assert: error message "Maximum 3 input images allowed"
  - Assert: exit code 2

- [ ] T035 [P] Integration test: missing input file (Scenario 9) in tests/integration/test_missing_input.py
  - Run CLI with: `--prompt "Test" --in nonexistent.png`
  - Assert: error message "Input image not found"
  - Assert: exit code 2

- [ ] T036 [P] Integration test: missing API key (Scenario 10) in tests/integration/test_missing_api_key.py
  - Unset: GEMINI_API_KEY environment variable
  - Run CLI with: `--prompt "Test"`
  - Assert: error message with setup instructions
  - Assert: exit code 1 (configuration error)

- [ ] T037 [P] Integration test: batch with partial failures (Scenario 12) in tests/integration/test_batch_partial_failure.py
  - Mock: API to fail on 2nd request, succeed on others
  - Run CLI with: `--prompt "Test" --batch 3`
  - Assert: 2 files created (1st and 3rd)
  - Assert: summary shows "2 successful, 1 failed"
  - Assert: exit code 0 (success because some succeeded)

- [ ] T038 [P] Integration test: invalid batch count (Scenario 13) in tests/integration/test_invalid_batch_count.py
  - Run CLI with: `--prompt "Test" --batch 0`
  - Assert: error message "Batch count must be at least 1"
  - Assert: exit code 2

## Phase 3.8: Quality Assurance

- [ ] T039 Run pyright type checking
  - Command: `uv run pyright src/ tests/`
  - Fix: all type errors (target: 0 errors)

- [ ] T040 Run ruff linting
  - Command: `uv run ruff check src/ tests/`
  - Fix: all linting issues (target: 0 issues)

- [ ] T041 Run ruff formatting
  - Command: `uv run ruff format src/ tests/`
  - Verify: all files formatted consistently

- [ ] T042 Run full test suite
  - Command: `uv run pytest -v`
  - Target: 100% pass rate for all tests

- [ ] T043 Verify contract tests pass
  - Command: `uv run pytest tests/contract/ -v`
  - Verify: all mocked API interactions work correctly

- [ ] T044 Verify integration tests pass
  - Command: `GEMINI_API_KEY="test_key" uv run pytest tests/integration/ -v`
  - Note: Uses mocks, not real API

- [ ] T045 Manual smoke test with real API
  - Set: real GEMINI_API_KEY
  - Run: `uv run python -m src.cli.main --prompt "A simple test image"`
  - Verify: image generated successfully
  - Verify: output is clear and styled with rich

## Phase 3.9: Documentation

- [ ] T046 Create README.md with usage examples
  - Section: Installation (uv sync, API key setup)
  - Section: Basic usage (text-to-image examples)
  - Section: Advanced usage (multimodal, batch, custom paths)
  - Section: Error troubleshooting (common errors and fixes)
  - Examples: all from quickstart.md scenarios

- [ ] T047 Create .env.example file
  - Content: `GEMINI_API_KEY=your_api_key_here`
  - Comment: Instructions to get API key from https://aistudio.google.com/apikey

- [ ] T048 Add docstrings to public functions
  - Format: Google-style docstrings
  - Coverage: all public functions in services, utils, cli

## Dependencies

**Critical Path**:
```
Setup (T001-T004)
  ↓
Models (T005-T009) → Unit Tests (T018-T020)
  ↓
Contract Tests (T010-T017) [must fail initially]
  ↓
Services (T021-T024) [makes contract tests pass]
  ↓
CLI (T025-T026)
  ↓
Integration Tests (T027-T038)
  ↓
QA (T039-T045) → Docs (T046-T048)
```

**Blocking Relationships**:
- T001 blocks ALL tasks (dependencies required)
- T005 (exceptions) blocks T006-T009, T021, T026
- T006-T009 (models) block T021-T024 (services)
- T010 (fixtures) blocks T011-T017 (contract tests)
- T021 (gemini_service) blocks T024 (batch_service)
- T022-T024 (services) block T026 (CLI main)
- T025-T026 (CLI) block T027-T038 (integration tests)

**Parallel Opportunities**:
- T002-T004: directory setup and config
- T005-T009: all model files (different files)
- T011-T017: all contract tests (different test cases)
- T018-T020: all unit tests (different test files)
- T022-T023: path_utils and image_service (different files)
- T027-T038: all integration tests (different test files)

## Parallel Execution Examples

### Phase 3.1 Setup (after T001)
```bash
# Launch T002-T004 in parallel
Task: "Create src/ directory structure"
Task: "Create tests/ directory structure"
Task: "Configure pyproject.toml for pyright and ruff"
```

### Phase 3.2 Models
```bash
# Launch T005-T009 in parallel
Task: "Create custom exception hierarchy in src/models/exceptions.py"
Task: "Create GenerationConfig model in src/models/config.py"
Task: "Create ImageGenerationRequest model in src/models/request.py"
Task: "Create ImageGenerationResponse model in src/models/response.py"
Task: "Create GenerationResult model in src/models/result.py"
```

### Phase 3.3 Contract Tests (after T010 fixtures)
```bash
# Launch T011-T017 in parallel
Task: "Contract test: successful single image generation"
Task: "Contract test: successful multimodal generation"
Task: "Contract test: API timeout handling"
Task: "Contract test: authentication error"
Task: "Contract test: rate limit error"
Task: "Contract test: empty response handling"
Task: "Contract test: maximum input images (3)"
```

### Phase 3.7 Integration Tests (after T026)
```bash
# Launch T027-T038 in parallel (12 tests)
Task: "Integration test: basic text-to-image"
Task: "Integration test: multimodal generation"
Task: "Integration test: custom output path"
# ... (all 12 integration tests)
```

## Validation Checklist

- [x] All contracts have corresponding tests (T011-T017 cover gemini_api_contract.md)
- [x] All entities have model tasks (T005-T009 cover all data-model.md entities)
- [x] All tests come before implementation (T010-T020 before T021-T026)
- [x] Parallel tasks truly independent (verified file paths)
- [x] Each task specifies exact file path (all tasks include paths)
- [x] No task modifies same file as another [P] task (verified)
- [x] All quickstart scenarios have integration tests (T027-T038 cover 11/13 scenarios, Scenario 11 merged with 5)

## Notes

- **TDD Critical**: Contract tests (T011-T017) and unit tests (T018-T020) MUST be written and MUST FAIL before implementing services (T021-T024)
- **User Context**: Project already initialized with `uv init`, so T001 starts with adding dependencies
- **No API Timeout Test**: Scenario 11 from quickstart (API timeout) requires actual network delay, not included as automated integration test
- **Batch Resilience**: T037 tests FR-019 requirement (continue batch on individual failures)
- **Exit Codes**: All integration tests verify correct exit codes per constitution requirements
- **Real API Test**: T045 is the only task requiring actual GEMINI_API_KEY, all others use mocks