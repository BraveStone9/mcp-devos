import pytest

import security
from security import SecurityError, check_readable_file, resolve_safe_path


@pytest.fixture
def sandbox(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "app.py").write_text("print('hello')")
    (root / "sub").mkdir()
    (root / "sub" / "notes.txt").write_text("notes")
    (tmp_path / "secret.txt").write_text("top secret")
    return root


def test_relative_path_inside_root_is_allowed(sandbox):
    assert resolve_safe_path("app.py", sandbox) == (sandbox / "app.py").resolve()


def test_nested_path_inside_root_is_allowed(sandbox):
    assert resolve_safe_path("sub/notes.txt", sandbox) == (sandbox / "sub" / "notes.txt").resolve()


def test_root_itself_is_allowed(sandbox):
    assert resolve_safe_path(".", sandbox) == sandbox.resolve()


def test_parent_traversal_is_blocked(sandbox):
    with pytest.raises(SecurityError):
        resolve_safe_path("../secret.txt", sandbox)


def test_deep_traversal_is_blocked(sandbox):
    with pytest.raises(SecurityError):
        resolve_safe_path("sub/../../secret.txt", sandbox)


def test_absolute_path_outside_root_is_blocked(sandbox, tmp_path):
    with pytest.raises(SecurityError):
        resolve_safe_path(str(tmp_path / "secret.txt"), sandbox)


def test_absolute_path_inside_root_is_allowed(sandbox):
    assert resolve_safe_path(str(sandbox / "app.py"), sandbox) == (sandbox / "app.py").resolve()


def test_sibling_folder_with_shared_prefix_is_blocked(sandbox, tmp_path):
    sibling = tmp_path / "root_evil"
    sibling.mkdir()
    (sibling / "data.txt").write_text("x")
    with pytest.raises(SecurityError):
        resolve_safe_path(str(sibling / "data.txt"), sandbox)


def test_null_byte_path_is_blocked(sandbox):
    with pytest.raises(SecurityError):
        resolve_safe_path("app.py\x00.txt", sandbox)


def test_symlink_escaping_root_is_blocked(sandbox, tmp_path):
    link = sandbox / "link.txt"
    try:
        link.symlink_to(tmp_path / "secret.txt")
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation not permitted on this system")
    with pytest.raises(SecurityError):
        resolve_safe_path("link.txt", sandbox)


def test_readable_file_is_returned(sandbox):
    assert check_readable_file("app.py", sandbox) == (sandbox / "app.py").resolve()


def test_directory_is_not_a_readable_file(sandbox):
    with pytest.raises(SecurityError):
        check_readable_file("sub", sandbox)


def test_missing_file_is_rejected(sandbox):
    with pytest.raises(SecurityError):
        check_readable_file("missing.py", sandbox)


def test_disallowed_extension_is_rejected(sandbox):
    (sandbox / "tool.exe").write_bytes(b"MZ")
    with pytest.raises(SecurityError):
        check_readable_file("tool.exe", sandbox)


def test_file_without_extension_is_rejected(sandbox):
    (sandbox / "Makefile").write_text("all:")
    with pytest.raises(SecurityError):
        check_readable_file("Makefile", sandbox)


def test_oversized_file_is_rejected(sandbox, monkeypatch):
    monkeypatch.setattr(security, "MAX_FILE_SIZE_BYTES", 10)
    (sandbox / "big.txt").write_text("x" * 100)
    with pytest.raises(SecurityError):
        check_readable_file("big.txt", sandbox)
