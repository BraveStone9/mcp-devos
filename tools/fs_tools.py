from security import check_readable_file, resolve_safe_path


def list_directory(path="."):
    resolved = resolve_safe_path(path)

    if not resolved.is_dir():
        raise NotADirectoryError(f"Not a directory: {path!r}")

    entries = []
    for entry in sorted(resolved.iterdir(), key=lambda e: e.name.lower()):
        entries.append({
            "name": entry.name,
            "type": "directory" if entry.is_dir() else "file",
        })

    return entries


def read_file(filepath):
    resolved = check_readable_file(filepath)
    return resolved.read_text(encoding="utf-8", errors="replace")
