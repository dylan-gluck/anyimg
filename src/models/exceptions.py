"""Custom exception hierarchy for anyimg CLI."""


class AnyImgError(Exception):
    """Base exception for all anyimg errors."""

    exit_code: int = 1
    remediation: str = ""

    def __init__(self, message: str, remediation: str = "") -> None:
        super().__init__(message)
        self.message = message
        if remediation:
            self.remediation = remediation


# Configuration Errors (exit code 1)
class ConfigurationError(AnyImgError):
    """Configuration-related errors."""

    exit_code = 1


class MissingAPIKeyError(ConfigurationError):
    """GEMINI_API_KEY environment variable not found."""

    def __init__(self) -> None:
        super().__init__(
            message="GEMINI_API_KEY environment variable not found",
            remediation="Set it with: export GEMINI_API_KEY=your_key",
        )


class InvalidConfigError(ConfigurationError):
    """Invalid configuration provided."""

    exit_code = 1


# Validation Errors (exit code 2)
class ValidationError(AnyImgError):
    """Input validation errors."""

    exit_code = 2


class InvalidInputImageError(ValidationError):
    """Input image file is invalid or inaccessible."""

    pass


class TooManyInputImagesError(ValidationError):
    """More than 3 input images provided."""

    def __init__(self, count: int) -> None:
        super().__init__(
            message=f"Maximum 3 input images allowed, got {count}",
            remediation="Provide at most 3 input images",
        )


class InvalidBatchCountError(ValidationError):
    """Batch count is invalid."""

    def __init__(self, count: int) -> None:
        super().__init__(
            message=f"Batch count must be at least 1, got {count}",
            remediation="Provide a positive batch count",
        )


# API Errors (exit code 3)
class APIError(AnyImgError):
    """Gemini API errors."""

    exit_code = 3


class APITimeoutError(APIError):
    """API request timed out."""

    def __init__(self, timeout: int = 60) -> None:
        super().__init__(
            message=f"Request timed out after {timeout} seconds",
            remediation="Check your network connection and retry",
        )


class APIRateLimitError(APIError):
    """API rate limit exceeded."""

    def __init__(self) -> None:
        super().__init__(
            message="API rate limit exceeded",
            remediation="Wait a few minutes before retrying",
        )


class APIResponseError(APIError):
    """API returned invalid or empty response."""

    pass


# File System Errors (exit code 4)
class FileSystemError(AnyImgError):
    """File system operation errors."""

    exit_code = 4


class DirectoryCreationError(FileSystemError):
    """Failed to create output directory."""

    pass
