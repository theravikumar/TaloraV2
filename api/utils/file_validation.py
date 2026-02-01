# api/utils/file_validation.py
"""
File validation utilities
"""
import hashlib
import magic
from pathlib import Path
from fastapi import UploadFile
from api.utils.errors import FileValidationError, ERROR_MESSAGES
from api.config import get_settings

settings = get_settings()

MAX_FILE_SIZE = settings.max_upload_size_mb * 1024 * 1024  # Convert to bytes


async def validate_pdf(file: UploadFile) -> bytes:
    """
    Validate uploaded PDF file.
    
    Returns file content if valid, raises FileValidationError otherwise.
    """
    # Read file content
    content = await file.read()
    await file.seek(0)  # Reset file pointer
    
    # Check file size
    if len(content) > MAX_FILE_SIZE:
        raise FileValidationError(ERROR_MESSAGES["file_too_large"])
    
    # Check file type using magic numbers
    file_type = magic.from_buffer(content, mime=True)
    if file_type != "application/pdf":
        raise FileValidationError(ERROR_MESSAGES["invalid_format"])
    
    # Basic PDF structure validation
    if not content.startswith(b'%PDF'):
        raise FileValidationError(ERROR_MESSAGES["invalid_format"])
    
    return content


def calculate_file_hash(content: bytes) -> str:
    """Calculate SHA256 hash of file content"""
    return hashlib.sha256(content).hexdigest()


async def scan_virus(file_path: Path) -> bool:
    """
    Scan file for viruses using ClamAV.
    
    For now, returns True (safe) - ClamAV integration can be added if needed.
    Production: Use clamd library to connect to ClamAV daemon.
    """
    # TODO: Integrate with ClamAV if installed
    # import clamd
    # cd = clamd.ClamdUnixSocket()
    # result = cd.scan(str(file_path))
    # return result[str(file_path)][0] == 'OK'
    
    return True  # Assume safe for now
