from typing import Any, Dict, Optional
from fastapi import status

class OrigoError(Exception):
    def __init__(self, *, error_code: str, message: str, http_status: int, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.http_status = http_status
        self.details = details or {}

    def to_response(self) -> Dict[str, Any]:
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class ValidationFailedError(OrigoError):
    def __init__(self, *, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(error_code="VALIDATION_FAILED", message=message, http_status=status.HTTP_422_UNPROCESSABLE_CONTENT, details=details)


class JsonParsingError(OrigoError):
    def __init__(self, *, message: str = "Malformed JSON response from LLM", details: Optional[Dict[str, Any]] = None):
        super().__init__(error_code="JSON_PARSING_ERROR", message=message, http_status=status.HTTP_502_BAD_GATEWAY, details=details)


class SaveProjectError(OrigoError):
    def __init__(self, *, message: str = "Failed to save project", details: Optional[Dict[str, Any]] = None):
        super().__init__(error_code="SAVE_PROJECT_ERROR", message=message, http_status=status.HTTP_500_INTERNAL_SERVER_ERROR, details=details)


class NotFoundError(OrigoError):
    def __init__(self, *, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(error_code="NOT_FOUND", message=message, http_status=status.HTTP_404_NOT_FOUND, details=details)


class BadRequestError(OrigoError):
    def __init__(self, *, message: str = "Bad request", details: Optional[Dict[str, Any]] = None):
        super().__init__(error_code="BAD_REQUEST", message=message, http_status=status.HTTP_400_BAD_REQUEST, details=details)


class ZipError(OrigoError):
    def __init__(self, *, message: str = "Zip error", details: Optional[Dict[str, Any]] = None):
        super().__init__(error_code="ZIP_ERROR", message=message, http_status=status.HTTP_500_INTERNAL_SERVER_ERROR, details=details)


# Preview pipeline errors
class PreviewInputInvalidError(OrigoError):
    def __init__(self, *, message: str = "Preview input invalid", details: Optional[Dict[str, Any]] = None):
        super().__init__(error_code="PREVIEW_INPUT_INVALID", message=message, http_status=status.HTTP_400_BAD_REQUEST, details=details)


class PreviewNotFoundError(OrigoError):
    def __init__(self, *, message: str = "Project not found during preview", details: Optional[Dict[str, Any]] = None):
        super().__init__(error_code="PREVIEW_NOT_FOUND", message=message, http_status=status.HTTP_404_NOT_FOUND, details=details)


class PreviewMissingFieldsError(OrigoError):
    def __init__(self, *, message: str = "Missing required fields for preview", details: Optional[Dict[str, Any]] = None):
        super().__init__(error_code="PREVIEW_MISSING_FIELDS", message=message, http_status=status.HTTP_422_UNPROCESSABLE_CONTENT, details=details)


class PreviewUnexpectedError(OrigoError):
    def __init__(self, *, message: str = "Unexpected preview error", details: Optional[Dict[str, Any]] = None):
        super().__init__(error_code="PREVIEW_UNEXPECTED", message=message, http_status=status.HTTP_500_INTERNAL_SERVER_ERROR, details=details)


class PreviewTransformFailedError(OrigoError):
    def __init__(self, *, message: str = "esbuild transform failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(error_code="PREVIEW_TRANSFORM_FAILED", message=message, http_status=status.HTTP_502_BAD_GATEWAY, details=details)
