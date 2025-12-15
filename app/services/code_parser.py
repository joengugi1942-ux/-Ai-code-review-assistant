from app.schemas.file import ParsedFile
from app.utils.language_detect import detect_language


class CodeParser:
    def parse(self, filename: str, content: str) -> ParsedFile:
        language = detect_language(filename, content)
        return ParsedFile(filename=filename, language=language, content=content)



