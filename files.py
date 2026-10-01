import re
import uuid
from pathlib import Path


def safe_filename(value: str, extension: str = "png") -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-").lower()
    cleaned = cleaned[:80] or "comic-panel"
    return f"{cleaned}-{uuid.uuid4().hex[:10]}.{extension.lstrip('.')}"


def relative_static_url(path: Path, static_dir: Path) -> str:
    relative = path.resolve().relative_to(static_dir.resolve())
    return "/static/" + "/".join(relative.parts)
