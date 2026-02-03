# anyimg - CLI for Gemini 3 Pro Image Generation

CLI for generating images using `Google Gemini 3 Pro Image Preview`.

## Features

- **Text-to-image generation**: Create images from text prompts
- **Multimodal input**: Use up to 3 reference images for context-aware generation
- **Batch generation**: Generate multiple images in one command
- **Batch API support**: Use JSONL files for efficient batch processing
- **Aspect ratio & resolution control**: Customize image dimensions
- **Smart file naming**: Automatic timestamped filenames or custom paths
- **File collision handling**: Auto-rename with numeric suffixes to prevent overwrites
- **Rich CLI output**: Styled terminal output with clear success/error messages

## Installation

### Global Installation (Recommended)

1. **Prerequisites**: Python 3.11+ and [UV](https://github.com/astral-sh/uv)

2. **Install globally**:
```bash
git clone https://github.com/dylan-gluck/anyimg
cd anyimg
uv tool install .
```

3. **Set up API key**:
Get your API key from [Google AI Studio](https://aistudio.google.com/apikey), then:
```bash
export GEMINI_API_KEY="your_api_key_here"
```

After installation, the `anyimg` command is available globally from any directory.

To uninstall: `uv tool uninstall anyimg`

### Local Development Installation

1. **Prerequisites**: Python 3.11+ and [UV](https://github.com/astral-sh/uv)

2. **Clone and install**:
```bash
git clone https://github.com/dylan-gluck/anyimg
cd anyimg
uv sync
```

3. **Set up API key**:
Get your API key from [Google AI Studio](https://aistudio.google.com/apikey), then:
```bash
export GEMINI_API_KEY="your_api_key_here"
```

## Usage

The examples below use the global `anyimg` command. If you installed for local development, replace `anyimg` with `uv run python -m src`.

### Basic text-to-image
```bash
anyimg --prompt "A serene mountain landscape at sunset"
```
Creates: `anyimg_20250930_143022.png` in current directory

### With reference images (multimodal)
```bash
anyimg \
  --prompt "Combine the styles of these images" \
  --in ref1.png,ref2.jpg
```
Supports up to 3 input images (PNG/JPEG/JPG formats only)

### Custom output path
```bash
anyimg \
  --prompt "A futuristic cityscape" \
  --out outputs/city.png
```
Creates `outputs/` directory if needed

### Batch generation
```bash
# With custom path (creates indexed files)
anyimg \
  --prompt "Abstract art with vibrant colors" \
  --out art.png \
  --batch 3
```
Creates: `art_1.png`, `art_2.png`, `art_3.png`

```bash
# With default naming (timestamped files)
anyimg \
  --prompt "Random abstract patterns" \
  --batch 3
```
Creates 3 files with unique timestamps

### With aspect ratio and resolution
```bash
# Generate a wide, high-resolution image
anyimg \
  --prompt "Cinematic landscape" \
  --aspect-ratio 21:9 \
  --resolution 4K
```

### Batch API mode (JSONL file)
```bash
# Create a JSONL file with batch requests
cat > batch_requests.jsonl << EOF
{"key": "request-1", "request": {"contents": [{"parts": [{"text": "A red sports car"}]}], "generation_config": {"responseModalities": ["TEXT", "IMAGE"]}}}
{"key": "request-2", "request": {"contents": [{"parts": [{"text": "A blue sports car"}]}], "generation_config": {"responseModalities": ["TEXT", "IMAGE"]}}}
EOF

# Process batch requests
anyimg --batch-file batch_requests.jsonl
```
Results are saved to `batch_results/` directory.

## Command-Line Options

| Option | Description | Required | Default |
|--------|-------------|----------|---------|
| `--prompt` | Text prompt for image generation | Yes | - |
| `--in` | Comma-separated input image paths (max 3) | No | None |
| `--out` | Output path for generated image | No | `anyimg_<timestamp>.png` |
| `--batch` | Number of images to generate | No | 1 |
| `--aspect-ratio` | Aspect ratio for generated image | No | auto |
| `--resolution` | Resolution for generated image | No | auto |
| `--batch-file` | JSONL file for batch API mode | No | - |

## Example Usage

```bash
# Halloween card with spooky theme
anyimg --in ghost.png,frankenstein.png,haunted_house.png --out spooky-card.png \
  "Spooky halloween card. Text to include: 'Have a SpoOoOky Halloween!'. Colors: Black, White, Orange, Purple. Size: 3x4"

# Batch generate 5 jack-o-lanterns
anyimg --batch 5 "Cartoon jack-o-lantern with glowing eyes on black background"
```

## Error Handling

The tool provides clear error messages with suggested fixes:

- **Exit code 0**: Success
- **Exit code 1**: Configuration error (e.g., missing API key)
- **Exit code 2**: Validation error (e.g., invalid file format)
- **Exit code 3**: API error (e.g., timeout, rate limit)
- **Exit code 4**: File system error (e.g., permission denied)

## Development

### Run tests
```bash
# All tests
uv run pytest -v

# Contract tests (mocked API)
uv run pytest tests/contract/ -v

# Integration tests
GEMINI_API_KEY="test_key" uv run pytest tests/integration/ -v

# Unit tests
uv run pytest tests/unit/ -v
```

### Type checking
```bash
uv run pyright src/ tests/
```

### Linting and formatting
```bash
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

## Project Structure

```
anyimg/
├── src/
│   ├── models/          # Pydantic models (config, request, response, exceptions)
│   ├── services/        # Core logic (Gemini API, image I/O, batch processing)
│   ├── cli/            # CLI argument parsing and main entry point
│   └── utils/          # Helper functions (path validation, timestamps)
├── tests/
│   ├── contract/       # API contract tests (mocked)
│   ├── integration/    # End-to-end workflow tests
│   └── unit/          # Unit tests for models
├── pyproject.toml     # UV project configuration
└── README.md          # This file
```

## Troubleshooting

### "GEMINI_API_KEY not found"
Set the environment variable:
```bash
export GEMINI_API_KEY="your_key"
```

### "Invalid input image format"
Only PNG and JPEG/JPG formats are supported for input images

### "Maximum 3 input images allowed"
The Gemini API supports up to 3 reference images per request

### "API rate limit exceeded"
Wait a few minutes before retrying, or reduce batch size

## References

- Gemini Image Generation: https://ai.google.dev/gemini-api/docs/image-generation
- Gemini Batch API: https://ai.google.dev/gemini-api/docs/batch-api
- Video Generation: https://ai.google.dev/gemini-api/docs/video
