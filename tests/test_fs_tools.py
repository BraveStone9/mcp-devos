import pytest

import security
from tools.fs_tools import list_directory, read_file


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    root = tmp_path / "root"
    root.mkdir()
    (root / "app.py").write_text("print('hello')")
    (root / "sub").mkdir()
    (root / "sub" / "notes.txt").write_text("notes")
    (tmp_path / "secret.txt").write_text("top secret")

    monkeypatch.setattr(security, "DEVOS_ROOT", root)
    return root


def test_list_directory_lists_files_and_dirs(sandbox):
    entries = list_directory(".")
    assert {"name": "app.py", "type": "file"} in entries
    assert {"name": "sub", "type": "directory"} in entries


def test_list_directory_is_sorted_case_insensitively(sandbox):
    (sandbox / "Zebra.txt").write_text("z")
    (sandbox / "apple.txt").write_text("a")
    names = [e["name"] for e in list_directory(".")]
    assert names == sorted(names, key=str.lower)


def test_list_directory_rejects_traversal(sandbox):
    with pytest.raises(security.SecurityError):
        list_directory("..")


def test_list_directory_rejects_file_as_path(sandbox):
    with pytest.raises(NotADirectoryError):
        list_directory("app.py")


def test_read_file_returns_contents(sandbox):
    assert read_file("app.py") == "print('hello')"


def test_read_file_rejects_traversal(sandbox):
    with pytest.raises(security.SecurityError):
        read_file("../secret.txt")


def test_read_file_rejects_directory(sandbox):
    with pytest.raises(security.SecurityError):
        read_file("sub")


def test_read_file_rejects_missing_file(sandbox):
    with pytest.raises(security.SecurityError):
        read_file("missing.py")
