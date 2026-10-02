from security import check_readable_file


def read_log(filename, lines=50, level_filter=None):
    resolved = check_readable_file(filename)
    content = resolved.read_text(encoding="utf-8", errors="replace")
    all_lines = content.splitlines()

    if level_filter:
        needle = level_filter.upper()
        all_lines = [line for line in all_lines if needle in line.upper()]

    return all_lines[-lines:]
