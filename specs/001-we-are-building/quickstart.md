# Quickstart: Gemini 2.5 Flash Image Generation CLI

**Feature**: 001-we-are-building
**Date**: 2025-09-30
**Purpose**: Step-by-step validation of all user scenarios from spec.md

---

## Prerequisites

1. **Python 3.11+** installed
2. **UV** installed (for dependency management)
3. **Gemini API key** from https://aistudio.google.com/apikey
4. **Repository cloned** and in project root directory

---

## Setup

```bash
# 1. Set API key environment variable
export GEMINI_API_KEY="your_api_key_here"

# 2. Install dependencies with UV
uv sync

# 3. Verify installation
uv run python -m src.cli.main --help
```

**Expected output**: Help text showing available flags (--prompt, --in, --out, --batch)

---

## Scenario 1: Basic Text-to-Image Generation

**Acceptance Criterion**: FR-001, FR-006
> Given the user provides only a text prompt, When they run the CLI tool, Then an image is generated and saved as `anyimg_<timestamp>.png` in the current directory

### Steps

```bash
# Generate image with text prompt only
uv run python -m src.cli.main --prompt "A serene mountain landscape at sunset"
```

### Validation

1. **Output message**: `✓ Generated image: anyimg_20250930_HHMMSS.png`
2. **File exists**: `ls anyimg_*.png` shows the generated file
3. **File is valid PNG**: `file anyimg_*.png` reports "PNG image data"
4. **Exit code**: `echo $?` returns `0`

---

## Scenario 2: Multimodal Generation (Text + Images)

**Acceptance Criterion**: FR-002, FR-004
> Given the user provides a prompt and 1-3 input images, When they run the CLI tool, Then an image is generated using the prompt and input images as context

### Setup

```bash
# Create test input images (or use your own PNG/JPEG files)
# For this test, assume we have ref1.png and ref2.jpg
```

### Steps

```bash
# Generate image with prompt and 2 reference images
uv run python -m src.cli.main \
  --prompt "Combine the styles of these two images" \
  --in ref1.png,ref2.jpg
```

### Validation

1. **Output message**: Confirms image generation with timestamp
2. **File exists**: New PNG file in current directory
3. **Exit code**: `0`

---

## Scenario 3: Custom Output Path

**Acceptance Criterion**: FR-007, FR-008, FR-014
> Given the user specifies a custom output path, When they run the CLI tool, Then the image is saved to that exact path

### Steps

```bash
# Generate with custom output path (directory doesn't exist yet)
uv run python -m src.cli.main \
  --prompt "A futuristic cityscape" \
  --out outputs/city.png
```

### Validation

1. **Directory created**: `outputs/` directory now exists (FR-014)
2. **File exists**: `ls outputs/city.png` shows the file
3. **Output message**: `✓ Generated image: outputs/city.png`
4. **Exit code**: `0`

---

## Scenario 4: Batch Generation with Custom Output Path

**Acceptance Criterion**: FR-009, FR-010
> Given the user specifies a batch count of N and a custom output path, When they run the CLI tool, Then N images are generated and saved with indexed filenames

### Steps

```bash
# Generate 3 images in batch mode
uv run python -m src.cli.main \
  --prompt "Abstract art with vibrant colors" \
  --out art.png \
  --batch 3
```

### Validation

1. **Files exist**: `ls art_*.png` shows `art_1.png`, `art_2.png`, `art_3.png`
2. **Output message**: Shows progress and final count (3 successful)
3. **Exit code**: `0`

---

## Scenario 5: Batch Generation without Custom Path

**Acceptance Criterion**: FR-011
> Given the user specifies a batch count of N without a custom output path, When they run the CLI tool, Then N images are generated with timestamped filenames

### Steps

```bash
# Generate 3 images with default naming
uv run python -m src.cli.main \
  --prompt "Random abstract patterns" \
  --batch 3
```

### Validation

1. **Files exist**: `ls anyimg_*.png` shows 3 files with different timestamps
2. **Filenames unique**: Each file has a unique timestamp
3. **Output message**: Lists all 3 generated files
4. **Exit code**: `0`

---

## Scenario 6: File Collision Handling

**Acceptance Criterion**: FR-015
> System MUST auto-rename output files with numeric suffix when the target path already exists

### Setup

```bash
# Create an existing file
touch myimage.png
```

### Steps

```bash
# Try to generate to same path
uv run python -m src.cli.main \
  --prompt "A new image" \
  --out myimage.png
```

### Validation

1. **Original file untouched**: `myimage.png` still empty (from touch)
2. **New file created**: `myimage_1.png` exists with actual image data
3. **Output message**: `✓ Generated image: myimage_1.png` (shows renamed path)
4. **Exit code**: `0`

---

## Scenario 7: Invalid Input Image Format

**Acceptance Criterion**: FR-016
> System MUST accept PNG and JPEG/JPG formats for input images and reject other formats with a clear error message

### Setup

```bash
# Create a non-image file
echo "not an image" > test.txt
```

### Steps

```bash
# Try to use text file as input image
uv run python -m src.cli.main \
  --prompt "Test" \
  --in test.txt
```

### Validation

1. **Error message**: `Error: Invalid input image format: test.txt. Only PNG and JPEG/JPG are supported.`
2. **Remediation shown**: Message suggests valid formats
3. **Exit code**: `2` (validation error)
4. **No API call made**: Image generation does not occur

---

## Scenario 8: Too Many Input Images

**Acceptance Criterion**: FR-003
> System MUST reject requests with more than 3 input images

### Setup

```bash
# Assume we have 4 image files: img1.png, img2.png, img3.png, img4.png
```

### Steps

```bash
# Try to provide 4 input images
uv run python -m src.cli.main \
  --prompt "Test" \
  --in img1.png,img2.png,img3.png,img4.png
```

### Validation

1. **Error message**: `Error: Maximum 3 input images allowed, got 4`
2. **Exit code**: `2` (validation error)
3. **No API call made**: Validation fails before API request

---

## Scenario 9: Missing Input Image File

**Acceptance Criterion**: FR-004
> System MUST validate that all specified input image files exist and are readable before making the API request

### Steps

```bash
# Try to use non-existent file
uv run python -m src.cli.main \
  --prompt "Test" \
  --in nonexistent.png
```

### Validation

1. **Error message**: `Error: Input image not found: nonexistent.png`
2. **Exit code**: `2` (validation error)
3. **No API call made**: Validation fails before API request

---

## Scenario 10: Missing API Key

**Acceptance Criterion**: FR-005, Constitution IV (Environment-Based Configuration)
> System MUST check for required environment variables at startup and fail fast with helpful messages if missing

### Steps

```bash
# Unset API key
unset GEMINI_API_KEY

# Try to generate image
uv run python -m src.cli.main --prompt "Test"
```

### Validation

1. **Error message**: `Error: GEMINI_API_KEY environment variable not found`
2. **Remediation shown**: `Fix: Set it with: export GEMINI_API_KEY=your_key`
3. **Exit code**: `1` (configuration error)
4. **No API call made**: Fails immediately on startup

---

## Scenario 11: API Timeout

**Acceptance Criterion**: FR-017
> System MUST timeout API requests to Gemini 2.5 Flash after 60 seconds and display a clear error message

### Steps (Simulated)

```bash
# This scenario requires network delay simulation or mock
# In production: request takes > 60 seconds
uv run python -m src.cli.main --prompt "Complex scene with many details"
```

### Expected Validation (if timeout occurs)

1. **Error message**: `Error: Request timed out after 60 seconds`
2. **Remediation shown**: `Fix: Check your network connection and retry`
3. **Exit code**: `3` (API error)

---

## Scenario 12: Batch with Partial Failures

**Acceptance Criterion**: FR-019, FR-020
> System MUST save all successfully generated images in batch mode and continue processing despite individual request failures. System MUST report which batch items succeeded and which failed at completion.

### Steps (Simulated with mock)

```bash
# Simulate batch where 2nd request fails (requires mock setup in test environment)
# In real use: network issues might cause intermittent failures
uv run python -m src.cli.main \
  --prompt "Test batch resilience" \
  --batch 3
```

### Expected Validation

1. **Some files exist**: `anyimg_*.png` files for successful generations
2. **Output message**:
   - `✓ 2 images generated successfully`
   - `✗ 1 failed: [error details]`
   - Lists successful file paths
3. **Exit code**: `0` (success, because some succeeded per FR-019)

---

## Scenario 13: Invalid Batch Count

**Acceptance Criterion**: Edge case - batch count must be >= 1

### Steps

```bash
# Try batch count of 0
uv run python -m src.cli.main \
  --prompt "Test" \
  --batch 0
```

### Validation

1. **Error message**: `Error: Batch count must be at least 1, got 0`
2. **Exit code**: `2` (validation error)

---

## Success Criteria Summary

✅ All 13 scenarios pass validation
✅ Error messages are clear and actionable
✅ Exit codes are correct (0=success, 1=config, 2=validation, 3=API, 4=filesystem)
✅ No API calls made for validation errors
✅ Files are created in expected locations with correct naming
✅ Batch mode handles failures gracefully

---

## Running Integration Tests

After implementation, run the full test suite:

```bash
# Unit tests
uv run pytest tests/unit/ -v

# Contract tests (with mocks)
uv run pytest tests/contract/ -v

# Integration tests (requires API key)
GEMINI_API_KEY="your_key" uv run pytest tests/integration/ -v

# All tests
uv run pytest -v

# Type checking
uv run pyright src/ tests/

# Linting
uv run ruff check src/ tests/
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'src'"

**Fix**: Run commands with `uv run python -m src.cli.main` (not `python src/cli/main.py`)

### Issue: "GEMINI_API_KEY not found"

**Fix**: Export the environment variable in your current shell session

### Issue: "Permission denied" when writing files

**Fix**: Check directory permissions or specify output path in writable directory

### Issue: API rate limit errors

**Fix**: Wait a few minutes before retrying. Consider reducing batch count.