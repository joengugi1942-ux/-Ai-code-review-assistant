from pydantic import BaseModel


class UploadedFileMetadata(BaseModel):
    filename: str
    language: str | None = None
    size_bytes: int | None = None


class ParsedFile(BaseModel):
    filename: str
    language: str
    content: str



