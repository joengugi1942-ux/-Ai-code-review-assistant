"""
File schemas for uploaded file metadata and parsed files.
"""

from pydantic import BaseModel


class UploadedFileMetadata(BaseModel):
    """Metadata for an uploaded file."""

    filename: str
    language: str | None = None
    size_bytes: int | None = None


class ParsedFile(BaseModel):
    """A parsed code file with detected language."""

    filename: str
    language: str
    content: str



