from pathlib import Path


def detect_language(filename: str, content: str | None = None) -> str:
    suffix = Path(filename).suffix.lower()
    mapping = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".java": "java",
        ".go": "go",
        ".rb": "ruby",
        ".php": "php",
    }
    return mapping.get(suffix, "unknown")



