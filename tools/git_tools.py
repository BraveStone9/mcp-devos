import subprocess

from config import DEVOS_ROOT


class GitError(Exception):
    pass


def _run_git(args):
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=DEVOS_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except FileNotFoundError as exc:
        raise GitError("git is not installed or not on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise GitError("git command timed out") from exc

    if result.returncode != 0:
        raise GitError(result.stderr.strip() or "git command failed")

    return result.stdout


def get_git_status():
    return _run_git(["status", "--short"])


def get_git_diff():
    return _run_git(["diff"])


def get_git_log(n=10):
    return _run_git(["log", f"-{int(n)}", "--oneline"])
