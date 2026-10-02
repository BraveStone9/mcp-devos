import pytest

import security
from tools.log_tools import read_log

SAMPLE_LOG = """\
2026-01-01 10:00:00 INFO Starting app
2026-01-01 10:00:01 INFO Connected to db
2026-01-01 10:00:02 WARN Slow query detected
2026-01-01 10:00:03 ERROR Division by zero in app.py:12
2026-01-01 10:00:04 INFO Request handled
2026-01-01 10:00:05 ERROR Unhandled exception in app.py:12
"""


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    root = tmp_path / "root"
    root.mkdir()
    (root / "app.log").write_text(SAMPLE_LOG)
    (tmp_path / "secret.log").write_text("outside root")

    monkeypatch.setattr(security, "DEVOS_ROOT", root)
    return root


def test_read_log_returns_all_lines_within_limit(sandbox):
    lines = read_log("app.log", lines=50)
    assert len(lines) == 6
    assert lines[0].endswith("Starting app")


def test_read_log_respects_line_limit(sandbox):
    lines = read_log("app.log", lines=2)
    assert len(lines) == 2
    assert lines[-1].endswith("Unhandled exception in app.py:12")


def test_read_log_filters_by_level(sandbox):
    lines = read_log("app.log", lines=50, level_filter="ERROR")
    assert len(lines) == 2
    assert all("ERROR" in line for line in lines)


def test_read_log_filter_is_case_insensitive(sandbox):
    lines = read_log("app.log", lines=50, level_filter="error")
    assert len(lines) == 2


def test_read_log_filter_combined_with_limit(sandbox):
    lines = read_log("app.log", lines=1, level_filter="ERROR")
    assert len(lines) == 1
    assert "Unhandled exception" in lines[0]


def test_read_log_rejects_traversal(sandbox):
    with pytest.raises(security.SecurityError):
        read_log("../secret.log")


def test_read_log_rejects_missing_file(sandbox):
    with pytest.raises(security.SecurityError):
        read_log("missing.log")
