from mcp.server.mcpserver import MCPServer

from tools.fs_tools import list_directory, read_file
from tools.git_tools import (
    get_git_diff,
    get_git_log,
    get_git_status,
    get_last_commit_diff,
)
from tools.log_tools import read_log

mcp = MCPServer("devos")


@mcp.tool()
def list_dir(path: str = ".") -> list[dict]:
    """List the files and directories at a path inside the sandboxed project root."""
    return list_directory(path)


@mcp.tool()
def read_source_file(filepath: str) -> str:
    """Read the text contents of a file inside the sandboxed project root."""
    return read_file(filepath)


@mcp.tool()
def git_status() -> str:
    """Show the working tree status of the sandboxed git repository."""
    return get_git_status()


@mcp.tool()
def git_diff() -> str:
    """Show uncommitted changes in the sandboxed git repository."""
    return get_git_diff()


@mcp.tool()
def git_log(count: int = 10) -> str:
    """Show the most recent commits in the sandboxed git repository."""
    return get_git_log(count)


@mcp.tool()
def git_last_commit_diff() -> str:
    """Show what changed in the most recent commit of the sandboxed git repository."""
    return get_last_commit_diff()


@mcp.tool()
def read_log_file(filename: str, lines: int = 50, level_filter: str | None = None) -> list[str]:
    """Read the last N lines of a log file, optionally filtered by severity level (e.g. ERROR, WARN)."""
    return read_log(filename, lines=lines, level_filter=level_filter)


if __name__ == "__main__":
    mcp.run(transport="stdio")
