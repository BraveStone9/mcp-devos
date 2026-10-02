import subprocess

import pytest

import tools.git_tools as git_tools
from tools.git_tools import GitError, get_git_diff, get_git_log, get_git_status


def _git(root, *args):
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init")
    _git(root, "config", "user.email", "test@example.com")
    _git(root, "config", "user.name", "Test")

    (root / "app.py").write_text("print('v1')")
    _git(root, "add", "app.py")
    _git(root, "commit", "-m", "initial commit")

    monkeypatch.setattr(git_tools, "DEVOS_ROOT", root)
    return root


def test_git_status_reports_clean_repo(repo):
    assert get_git_status() == ""


def test_git_status_reports_modified_file(repo):
    (repo / "app.py").write_text("print('v2')")
    status = get_git_status()
    assert "app.py" in status


def test_git_diff_shows_change(repo):
    (repo / "app.py").write_text("print('v2')")
    diff = get_git_diff()
    assert "v2" in diff


def test_git_diff_empty_when_no_changes(repo):
    assert get_git_diff() == ""


def test_git_log_shows_commit(repo):
    log = get_git_log()
    assert "initial commit" in log


def test_git_log_respects_count(repo):
    (repo / "b.py").write_text("x = 1")
    _git(repo, "add", "b.py")
    _git(repo, "commit", "-m", "second commit")

    log = get_git_log(1)
    assert "second commit" in log
    assert "initial commit" not in log


def test_git_command_fails_outside_a_repo(tmp_path, monkeypatch):
    non_repo = tmp_path / "not_a_repo"
    non_repo.mkdir()
    monkeypatch.setattr(git_tools, "DEVOS_ROOT", non_repo)

    with pytest.raises(GitError):
        get_git_status()
