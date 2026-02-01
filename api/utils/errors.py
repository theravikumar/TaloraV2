# api/utils/errors.py
"""
Custom error classes
"""

class TaloraError(Exception):
    """Base exception for Talora API"""
    pass


class FileValidationError(TaloraError):
    """File validation failed"""
    pass


class ParsingError(TaloraError):
    """Resume parsing failed"""
    pass


class AuthenticationError(TaloraError):
    """Authentication failed"""
    pass


class QuotaExceededError(TaloraError):
    """LLM quota exceeded"""
    pass


# User-friendly error messages
ERROR_MESSAGES = {
    "file_too_large": "File size must be under 5MB",
    "invalid_format": "Please upload a PDF file",
    "virus_detected": "File failed security scan",
    "parse_failed": "Unable to process resume. Please try again.",
    "quota_exceeded": "Service temporarily unavailable. Please try again in a few minutes.",
    "duplicate_email": "Email already registered",
    "invalid_credentials": "Invalid email or password",
    "max_resumes": "Maximum 5 resumes allowed. Please delete one to upload new.",
    "resume_not_found": "Resume not found",
    "unauthorized": "Authentication required",
}
