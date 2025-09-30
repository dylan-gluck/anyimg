# Data Model: Gemini 2.5 Flash Image Generation CLI

**Feature**: 001-we-are-building
**Date**: 2025-09-30
**Status**: Complete

## Overview

This document defines the core data structures for the anyimg CLI tool. All models use Pydantic for runtime validation and type safety.

## Core Entities

### 1. GenerationConfig

**Purpose**: Validates and stores CLI configuration from user arguments

**Fields**:
- `prompt: str` - Text prompt for image generation (required)
- `input_images: list[Path]` - List of 0-3 input image paths (default: empty list)
- `output_path: Path | None` - Custom output path (default: None, generates timestamped)
- `batch_count: int` - Number of images to generate (default: 1, min: 1)
- `api_key: str` - Gemini API key from environment

**Validation Rules**:
- `prompt`: Must be non-empty string, stripped of whitespace
- `input_images`: Maximum 3 items
- Each image path: Must exist, must be file, suffix in ['.png', '.jpg', '.jpeg']
- `batch_count`: Must be >= 1
- `api_key`: Must be non-empty, fail fast if missing from environment

**Example**:
```python
config = GenerationConfig(
    prompt="A futuristic city skyline at sunset",
    input_images=[Path("ref1.png"), Path("ref2.jpg")],
    output_path=Path("city.png"),
    batch_count=3,
    api_key=os.getenv("GEMINI_API_KEY")
)
```

---

### 2. ImageGenerationRequest

**Purpose**: Encapsulates a single generation request to Gemini API

**Fields**:
- `model: str` - Model identifier (constant: "gemini-2.5-flash-image-preview")
- `prompt: str` - Text prompt
- `input_images: list[PILImage.Image]` - Opened PIL Image objects (0-3)
- `timeout: int` - Request timeout in seconds (default: 60)

**Relationships**:
- Created from `GenerationConfig`
- Input images loaded from paths using PIL

**Example**:
```python
request = ImageGenerationRequest(
    model="gemini-2.5-flash-image-preview",
    prompt=config.prompt,
    input_images=[Image.open(p) for p in config.input_images],
    timeout=60
)
```

---

### 3. ImageGenerationResponse

**Purpose**: Wrapper for Gemini API response data

**Fields**:
- `image_data: bytes` - Raw PNG image bytes
- `success: bool` - Whether generation succeeded
- `error_message: str | None` - Error details if failed

**Validation Rules**:
- If `success=True`: `image_data` must be non-empty, `error_message` must be None
- If `success=False`: `error_message` must be non-empty, `image_data` may be empty

**Example**:
```python
# Success case
response = ImageGenerationResponse(
    image_data=b'\x89PNG\r\n...',
    success=True,
    error_message=None
)

# Failure case
response = ImageGenerationResponse(
    image_data=b'',
    success=False,
    error_message="API rate limit exceeded"
)
```

---

### 4. GenerationResult

**Purpose**: Represents the outcome of a single generation attempt (used in batch processing)

**Fields**:
- `index: int` - Batch index (0-based)
- `output_path: Path` - Where image was/would be saved
- `success: bool` - Whether this attempt succeeded
- `error_message: str | None` - Error details if failed
- `timestamp: datetime` - When generation was attempted

**Relationships**:
- Created per batch iteration
- Tracks both successful and failed generations per FR-019

**Example**:
```python
result = GenerationResult(
    index=0,
    output_path=Path("anyimg_20250930_143022.png"),
    success=True,
    error_message=None,
    timestamp=datetime.now()
)
```

---

## State Transitions

### File Naming State Machine

```
Initial State: User provides output_path or None

State 1: Determine base filename
  - If output_path provided → use it
  - If None → generate anyimg_{timestamp}.png

State 2: Check file existence
  - If file does NOT exist → use as-is (FINAL STATE)
  - If file exists → proceed to State 3

State 3: Auto-rename with suffix
  - Try {stem}_1{suffix}
  - If exists, try {stem}_2{suffix}
  - Repeat until non-existent path found (FINAL STATE)
```

**Example Flow**:
```
User input: --out image.png
Exists? Yes → Try image_1.png
Exists? Yes → Try image_2.png
Exists? No → Use image_2.png (FINAL)
```

---

### Batch Processing State Machine

```
State 1: Initialize (batch_count=N)
  - results = []
  - successful_count = 0
  - failed_count = 0

State 2: For each iteration i in range(N)
  - Generate output_path (with index if custom path provided)
  - Attempt API call
  - Create GenerationResult
  - If success: increment successful_count
  - If failure: increment failed_count
  - Append result to results
  - Continue to next iteration (do NOT abort)

State 3: Report results
  - Print successful_count, failed_count
  - List all output paths (successful)
  - List all errors (failed)
  - Exit code: 0 if any succeeded, non-zero if all failed
```

---

## Validation Summary

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| prompt | str | Yes | Non-empty, stripped |
| input_images | list[Path] | No | Max 3, exist, file, valid format |
| output_path | Path | No | Parent dir created if needed |
| batch_count | int | No | >= 1 |
| api_key | str | Yes | Non-empty, from env |

---

## Error Handling

### Custom Exception Hierarchy

```
AnyImgError (base)
├── ConfigurationError (exit 1)
│   ├── MissingAPIKeyError
│   └── InvalidConfigError
├── ValidationError (exit 2)
│   ├── InvalidInputImageError
│   ├── TooManyInputImagesError
│   └── InvalidBatchCountError
├── APIError (exit 3)
│   ├── APITimeoutError
│   ├── APIRateLimitError
│   └── APIResponseError
└── FileSystemError (exit 4)
    ├── FileNotFoundError
    ├── PermissionError
    └── DirectoryCreationError
```

Each exception includes:
- Clear error message describing what went wrong
- Suggested remediation (how to fix it)
- Appropriate exit code

---

## Implementation Notes

1. **Pydantic Field Validators**:
   - Use `@field_validator` for input_images path validation
   - Use `@model_validator(mode='after')` for cross-field validation
   - Use `Field(...)` for constraints (ge=1 for batch_count)

2. **Type Safety**:
   - All Path objects use `pathlib.Path`
   - PIL Images use `PIL.Image.Image` type hint
   - Use `list[T]` syntax (Python 3.11+)

3. **Environment Variables**:
   - Load in GenerationConfig constructor
   - Fail immediately if GEMINI_API_KEY missing
   - Provide clear error message with setup instructions

4. **Timestamp Format**:
   - Use `datetime.now().strftime('%Y%m%d_%H%M%S')` for file naming
   - Ensures chronological sorting and uniqueness within 1-second resolution
