from pathlib import Path

from config import ALLOWED_EXTENSIONS, DEVOS_ROOT, MAX_FILE_SIZE_BYTES


class SecurityError(Exception):
    pass


def resolve_safe_path(path, root=None):
    root = Path(root or DEVOS_ROOT).resolve()

    try:
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = root / candidate
        resolved = candidate.resolve()
    except (ValueError, OSError) as exc:
        raise SecurityError(f"Invalid path: {path!r}") from exc

    try:
        resolved.relative_to(root)
    except ValueError:
        raise SecurityError(f"Path is outside the allowed root: {path!r}")

    return resolved


def check_readable_file(path, root=None):
    resolved = resolve_safe_path(path, root)

    if not resolved.is_file():
        raise SecurityError(f"Not a file: {path!r}")

    if resolved.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise SecurityError(f"File type not allowed: {resolved.suffix or '(none)'}")

    if resolved.stat().st_size > MAX_FILE_SIZE_BYTES:
        limit_mb = MAX_FILE_SIZE_BYTES // (1024 * 1024)
        raise SecurityError(f"File exceeds the {limit_mb} MB size limit")

    return resolved
