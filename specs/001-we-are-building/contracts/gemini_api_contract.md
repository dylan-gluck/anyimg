# API Contract: Gemini 2.5 Flash Image Generation

**Service**: Google Gemini API (Image Generation)
**Endpoint**: Via `google.genai.Client()`
**Model**: `gemini-2.5-flash-image-preview`
**Date**: 2025-09-30

## Contract Overview

This document defines the expected behavior of the Gemini API integration for image generation. Contract tests will validate these expectations using mocked responses.

---

## Request Contract

### Method Signature
```python
client.models.generate_content(
    model: str,
    contents: str | list[str | PILImage.Image],
) -> Response
```

### Request Parameters

| Parameter | Type | Required | Constraints | Example |
|-----------|------|----------|-------------|---------|
| `model` | str | Yes | Must be "gemini-2.5-flash-image-preview" | "gemini-2.5-flash-image-preview" |
| `contents` | str or list | Yes | String prompt OR list of [prompt, img1, img2, ...] | "A sunset" OR ["A sunset", <PIL.Image>, <PIL.Image>] |

### Request Validations

**Pre-request validations** (performed by our code BEFORE API call):
1. Input images: Maximum 3 PIL Image objects
2. Prompt: Non-empty string
3. API key: Present in environment
4. Input image formats: PNG or JPEG/JPG only

---

## Response Contract

### Success Response Structure

```python
Response:
  candidates: list[Candidate]
    [0]:
      content:
        parts: list[Part]
          - inline_data:
              data: bytes  # PNG image data
              mime_type: "image/png"
```

### Response Fields

| Field Path | Type | Always Present | Description |
|------------|------|----------------|-------------|
| `response.candidates` | list | Yes | List of generation candidates |
| `response.candidates[0]` | Candidate | Yes | Primary candidate |
| `response.candidates[0].content` | Content | Yes | Content object |
| `response.candidates[0].content.parts` | list | Yes | List of content parts |
| `response.candidates[0].content.parts[i].inline_data` | InlineData | If image | Image data container |
| `response.candidates[0].content.parts[i].inline_data.data` | bytes | If image | Raw PNG bytes |

### Success Criteria

A response is considered successful if:
1. `response.candidates` is non-empty
2. `response.candidates[0].content.parts` contains at least one part with `inline_data`
3. `inline_data.data` is non-empty bytes
4. Image data can be opened with `PIL.Image.open(BytesIO(data))`

---

## Error Response Contract

### Error Types

| Error Type | HTTP/SDK Error | Trigger Condition | Expected Behavior |
|------------|----------------|-------------------|-------------------|
| Authentication Error | 401 Unauthorized | Invalid/missing API key | Raise ConfigurationError with message about setting GEMINI_API_KEY |
| Rate Limit Error | 429 Too Many Requests | API quota exceeded | Raise APIRateLimitError with message to wait and retry |
| Timeout Error | Network timeout | Request exceeds 60 seconds | Raise APITimeoutError with message to check network/retry |
| Invalid Request Error | 400 Bad Request | Malformed request | Raise APIResponseError with details from API |
| Server Error | 500 Internal Server Error | API service issue | Raise APIError with message to retry later |
| Network Error | Connection failed | No internet/DNS failure | Raise APIError with message to check connection |

### Error Response Structure

API errors from the SDK should be caught and re-raised as our custom exception types with user-friendly messages.

---

## Contract Test Specifications

### Test: Successful Single Image Generation

**Setup**:
- Mock `client.models.generate_content()` to return valid Response
- Response contains PNG image bytes

**Input**:
```python
request = ImageGenerationRequest(
    model="gemini-2.5-flash-image-preview",
    prompt="A blue sky",
    input_images=[],
    timeout=60
)
```

**Expected**:
- Method called with correct model and prompt
- Returns `ImageGenerationResponse(success=True, image_data=<bytes>)`
- Image data can be opened as PNG with PIL

---

### Test: Successful Multimodal Generation (Text + Images)

**Setup**:
- Mock `client.models.generate_content()` to return valid Response
- Input includes 2 PIL Image objects

**Input**:
```python
request = ImageGenerationRequest(
    model="gemini-2.5-flash-image-preview",
    prompt="Combine these styles",
    input_images=[<PIL.Image 1>, <PIL.Image 2>],
    timeout=60
)
```

**Expected**:
- Method called with list: [prompt, img1, img2]
- Returns `ImageGenerationResponse(success=True, image_data=<bytes>)`

---

### Test: API Timeout

**Setup**:
- Mock `client.models.generate_content()` to raise timeout exception after 60 seconds

**Input**:
```python
request = ImageGenerationRequest(
    model="gemini-2.5-flash-image-preview",
    prompt="A landscape",
    input_images=[],
    timeout=60
)
```

**Expected**:
- Raises `APITimeoutError`
- Error message includes "60 seconds" and suggests checking network

---

### Test: Authentication Error

**Setup**:
- Mock SDK to raise authentication error (401)

**Input**:
```python
# GEMINI_API_KEY environment variable not set or invalid
```

**Expected**:
- Raises `ConfigurationError` (specifically `MissingAPIKeyError`)
- Error message includes instructions: "Set GEMINI_API_KEY environment variable"

---

### Test: Rate Limit Error

**Setup**:
- Mock SDK to raise rate limit error (429)

**Input**:
```python
request = ImageGenerationRequest(
    model="gemini-2.5-flash-image-preview",
    prompt="An image",
    input_images=[],
    timeout=60
)
```

**Expected**:
- Raises `APIRateLimitError`
- Error message includes retry suggestion

---

### Test: Empty Response (No Image Data)

**Setup**:
- Mock SDK to return Response with no inline_data parts

**Input**:
```python
request = ImageGenerationRequest(
    model="gemini-2.5-flash-image-preview",
    prompt="Generate something",
    input_images=[],
    timeout=60
)
```

**Expected**:
- Raises `APIResponseError`
- Error message indicates no image data in response

---

### Test: Maximum Input Images (3)

**Setup**:
- Mock SDK to return valid Response

**Input**:
```python
request = ImageGenerationRequest(
    model="gemini-2.5-flash-image-preview",
    prompt="Mix these styles",
    input_images=[<PIL.Image 1>, <PIL.Image 2>, <PIL.Image 3>],
    timeout=60
)
```

**Expected**:
- Method called with list of length 4: [prompt, img1, img2, img3]
- Returns successful response

---

### Test: Exceeding Input Image Limit

**Setup**:
- Validation occurs BEFORE API call

**Input**:
```python
config = GenerationConfig(
    prompt="Test",
    input_images=[Path("1.png"), Path("2.png"), Path("3.png"), Path("4.png")],
    ...
)
```

**Expected**:
- Raises `TooManyInputImagesError` during config validation
- Error message: "Maximum 3 input images allowed, got 4"
- API is NOT called

---

## Implementation Notes

1. **Mock Strategy**:
   - Use `pytest-mock` to mock `genai.Client()` and its methods
   - Create fixture for mock client in `tests/contract/conftest.py`
   - Mock responses should use real Response object structure

2. **Timeout Handling**:
   - SDK timeout should be configured when available
   - Fallback: Wrap API calls in `asyncio.wait_for()` if SDK doesn't support timeout

3. **Error Mapping**:
   - Create mapping dict: SDK exception types → our exception types
   - Centralize in `src/services/api_error_handler.py`

4. **Retry Logic**:
   - Do NOT implement automatic retries (per FR-019, fail and continue in batch)
   - User can re-run command if desired

---

## Test File Location

Contract tests implementing these specifications:
- `tests/contract/test_gemini_api.py`

Each test must:
1. Mock the Gemini API client
2. Assert correct parameters passed to API
3. Assert correct exception type or response returned
4. Validate error messages are user-friendly