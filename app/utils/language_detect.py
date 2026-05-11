from pathlib import Path

_EXTENSION_MAP: dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".rb": "ruby",
    ".php": "php",
    ".cs": "csharp",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".c": "c",
    ".h": "c",
    ".hpp": "cpp",
    ".swift": "swift",
    ".scala": "scala",
    ".r": "r",
    ".sh": "bash",
    ".bash": "bash",
    ".zsh": "bash",
    ".fish": "bash",
    ".ps1": "powershell",
    ".sql": "sql",
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "scss",
    ".sass": "sass",
    ".less": "less",
    ".xml": "xml",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".json": "json",
    ".jsonc": "json",
    ".toml": "toml",
    ".md": "markdown",
    ".mdx": "markdown",
    ".tf": "terraform",
    ".tfvars": "terraform",
    ".lua": "lua",
    ".dart": "dart",
    ".ex": "elixir",
    ".exs": "elixir",
    ".erl": "erlang",
    ".hrl": "erlang",
    ".hs": "haskell",
    ".clj": "clojure",
    ".vim": "vimscript",
    ".dockerfile": "dockerfile",
}


def detect_language(filename: str, content: str | None = None) -> str:
    """Detect programming language from file extension. Returns 'unknown' if unrecognised."""
    name = Path(filename).name.lower()
    if name in ("dockerfile", "makefile", "gemfile", "rakefile", "procfile"):
        return name
    suffix = Path(filename).suffix.lower()
    return _EXTENSION_MAP.get(suffix, "unknown")
