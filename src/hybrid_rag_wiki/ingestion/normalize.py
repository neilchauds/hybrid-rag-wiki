from __future__ import annotations

from pathlib import PurePosixPath


def normalize_document_path(path: str) -> str:
    """Normalize incoming document path into canonical posix style."""
    cleaned = path.strip().replace("\\", "/")
    parts = [p for p in cleaned.split("/") if p not in ("", ".")]
    out_parts: list[str] = []
    for part in parts:
        if part == "..":
            if out_parts:
                out_parts.pop()
            continue
        out_parts.append(part)
    normalized = "/".join(out_parts)
    if normalized.endswith(".md"):
        return normalized
    return f"{normalized}.md"


def build_title_from_path(path: str) -> str:
    stem = PurePosixPath(path).stem
    return stem.replace("_", " ").strip() or "Untitled"


def normalize_link_target(source_path: str, raw_target: str) -> str | None:
    """
    Normalize internal markdown/wiki link target into canonical document path.

    Returns None for external links or anchors.
    """
    target = raw_target.strip()
    if not target:
        return None

    lowered = target.lower()
    if (
        lowered.startswith("http://")
        or lowered.startswith("https://")
        or lowered.startswith("mailto:")
        or lowered.startswith("tel:")
        or lowered.startswith("#")
    ):
        return None

    # Strip section fragments and query-like suffixes.
    target = target.split("#", 1)[0].split("?", 1)[0].strip()
    if not target:
        return None

    source_dir = str(PurePosixPath(source_path).parent)
    if source_dir == ".":
        source_dir = ""

    if "/" in target:
        candidate = normalize_document_path(target)
    else:
        if source_dir:
            candidate = normalize_document_path(f"{source_dir}/{target}")
        else:
            candidate = normalize_document_path(target)

    return candidate
