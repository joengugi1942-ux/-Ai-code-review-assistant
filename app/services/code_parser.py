"""
Code parser for extracting language and content from files.

Uses language detection to identify the programming language.
"""

from app.schemas.file import ParsedFile
from app.utils.language_detect import detect_language


class CodeParser:
    """Parser for extracting metadata from code files."""

    def parse(self, filename: str, content: str) -> ParsedFile:
        """
        Parse a code file and return metadata.
        
        Detects language and returns a ParsedFile with filename, language, and content.
        """
        language = detect_language(filename, content)
        return ParsedFile(filename=filename, language=language, content=content)




