import difflib


def generate_unified_diff(old: str, new: str, filename: str = "file") -> str:
    """Generate a unified diff between two text blobs."""
    old_lines = old.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
    )
    return "".join(diff)


def count_changed_lines(diff: str) -> tuple[int, int]:
    """Return (additions, deletions) from a unified diff string."""
    additions = sum(1 for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++"))
    deletions = sum(1 for line in diff.splitlines() if line.startswith("-") and not line.startswith("---"))
    return additions, deletions
