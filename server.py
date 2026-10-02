import logging
import os
import sys
from functools import wraps

from mcp.server.mcpserver import MCPServer

from config import DEVOS_ROOT
from tools.fs_tools import list_directory, read_file
from tools.git_tools import (
    get_git_diff,
    get_git_log,
    get_git_status,
    get_last_commit_diff,
)
from tools.log_tools import read_log

_formatter = logging.Formatter(
    fmt="%(asctime)s [server] %(message)s", datefmt="%H:%M:%S"
)
_handlers = [logging.StreamHandler(sys.stderr)]

_log_file = os.environ.get("DEVOS_LOG_FILE")
if _log_file:
    _handlers.append(logging.FileHandler(_log_file, mode="a", encoding="utf-8"))

for _handler in _handlers:
    _handler.setFormatter(_formatter)

logging.basicConfig(level=logging.INFO, handlers=_handlers)
logger = logging.getLogger("devos.server")

mcp = MCPServer("devos")


def logged_tool(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        call_args = ", ".join(
            [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
        )
        logger.info(f"-> {func.__name__}({call_args})")
        try:
            result = func(*args, **kwargs)
        except Exception as exc:
            logger.info(f"   {func.__name__} failed: {exc}")
            raise
        logger.info(f"<- {func.__name__} ok")
        return result

    return wrapper


@mcp.tool()
@logged_tool
def list_dir(path: str = ".") -> list[dict]:
    """List the files and directories at a path inside the sandboxed project root."""
    return list_directory(path)


@mcp.tool()
@logged_tool
def read_source_file(filepath: str) -> str:
    """Read the text contents of a file inside the sandboxed project root."""
    return read_file(filepath)


@mcp.tool()
@logged_tool
def git_status() -> str:
    """Show the working tree status of the sandboxed git repository."""
    return get_git_status()


@mcp.tool()
@logged_tool
def git_diff() -> str:
    """Show uncommitted changes in the sandboxed git repository."""
    return get_git_diff()


@mcp.tool()
@logged_tool
def git_log(count: int = 10) -> str:
    """Show the most recent commits in the sandboxed git repository."""
    return get_git_log(count)


@mcp.tool()
@logged_tool
def git_last_commit_diff() -> str:
    """Show what changed in the most recent commit of the sandboxed git repository."""
    return get_last_commit_diff()


@mcp.tool()
@logged_tool
def read_log_file(filename: str, lines: int = 50, level_filter: str | None = None) -> list[str]:
    """Read the last N lines of a log file, optionally filtered by severity level (e.g. ERROR, WARN)."""
    return read_log(filename, lines=lines, level_filter=level_filter)


if __name__ == "__main__":
    logger.info(f"Starting DevOS MCP server (sandbox root: {DEVOS_ROOT})")
    mcp.run(transport="stdio")
