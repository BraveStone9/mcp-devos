# Local Developer OS (MCP Server Integration)

A Model Context Protocol (MCP) server that gives an LLM client safe, sandboxed access to a local project: its files, its logs, and its Git history. It's built so an AI agent can investigate a real debugging problem — reading logs, inspecting source files, checking what changed recently in Git — without ever being able to touch anything outside one designated project folder.

**What this isn't:** This is a debugging assistant, not a code gatekeeper. It investigates problems that already exist rather than preventing bad code from being committed — there's no CI gate, no pre-commit hook, no scanning step.

Built using Claude Code as part of my normal development workflow.

Don't want to set it up yourself? See [SAMPLE_OUTPUT.md](SAMPLE_OUTPUT.md) for a real captured test run and a real captured debugging session, including exactly which tools the model called and in what order.

## How it works

The server exposes seven tools over MCP. A connected LLM client can call any of them, in any order, based on what it's trying to figure out:

| Tool | What it does |
|---|---|
| `list_dir` | Lists files and folders at a given path |
| `read_source_file` | Reads a file's contents |
| `git_status` | Shows uncommitted changes |
| `git_diff` | Shows the diff of uncommitted changes |
| `git_log` | Shows recent commit history |
| `git_last_commit_diff` | Shows exactly what the most recent commit changed |
| `read_log_file` | Reads the last N lines of a log file, optionally filtered by severity (e.g. `ERROR`) |

These are registered in [server.py](server.py), and all run over the `stdio` transport, which is the standard way local MCP servers talk to a client — the server doesn't know or care which client is on the other end.

Every one of these tools is a thin wrapper around a plain Python function in [tools/](tools/):
- [tools/fs_tools.py](tools/fs_tools.py) — file listing and reading
- [tools/git_tools.py](tools/git_tools.py) — Git status, diff, and log
- [tools/log_tools.py](tools/log_tools.py) — log file reading and filtering

## Security

Every filesystem and log tool call passes through [security.py](security.py) before it touches disk. This is the part that makes it safe to hand to an AI agent:

- **Sandboxing.** A single root directory is configured in [config.py](config.py) (`DEVOS_ROOT`, defaulting to the [demo/](demo/) folder). Every path is resolved to an absolute path and checked against that root — anything that resolves outside it (`../../` traversal, an absolute path elsewhere on disk, a symlink pointing out of the sandbox) is rejected before any file is opened.
- **Read-only.** There are no write or delete tools. The agent can look, but it can't change anything.
- **File-type and size limits.** Only a small set of text-based extensions are readable (`.py`, `.txt`, `.log`, `.md`, `.json`, `.yaml`, `.yml`, `.toml`, `.cfg`, `.ini`, `.csv`), and files over 5 MB are rejected, so the agent can't be pointed at a huge or unreadable binary file.
- **Safe Git execution.** [tools/git_tools.py](tools/git_tools.py) runs Git as a fixed argument list through `subprocess`, never through a shell string, so there's no command-injection path through a crafted input.

This is covered by 38 automated tests in [tests/](tests/), including attempts at path traversal, symlink escapes, disallowed file types, oversized files, and command injection via Git arguments — see [SAMPLE_OUTPUT.md](SAMPLE_OUTPUT.md) for the actual passing results.

## The demo

[demo/buggy_app/inventory.py](demo/buggy_app/inventory.py) is a small inventory script with one real bug: it indexes a 2-item list with index `2`, which is out of range. [demo/buggy_app/app.log](demo/buggy_app/app.log) contains the real traceback from running it. The project's own Git history shows a working version committed first, followed by the exact one-line change that introduced the bug — so `git_last_commit_diff` can reveal it, if the agent chooses to check.

[client_test/test_client.py](client_test/test_client.py) connects to the server and asks Gemini one question: *"Something is wrong with the inventory app. Can you investigate and tell me what's broken and why?"* Gemini isn't told which files exist or where to look — it has to call tools to find out, decide what to do next based on each result, and chain them together until it has enough information to answer. See [SAMPLE_OUTPUT.md](SAMPLE_OUTPUT.md) for exactly what it called and what it concluded.

## Setup

Requirements: Python 3.10+, Git, and a Gemini API key (a free one from Google AI Studio is enough).

```bash
# from inside this folder
python -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\Activate.ps1     # Windows PowerShell
pip install -r requirements.txt
```

Create a `.env` file in this folder with your API key:

```
GEMINI_API_KEY=your_key_here
```

## Running it

Run the test suite:

```bash
pytest -v
```

Run the debugging demo (this starts the server automatically — there's nothing else to launch first):

```bash
python client_test/test_client.py
```

You can change the question it asks by editing `DEBUG_PROMPT` in [client_test/test_client.py](client_test/test_client.py).

While it runs, both [client_test/test_client.py](client_test/test_client.py) and [server.py](server.py) log every step to the terminal in real time — the server starting, the session handshake, the available tools, and every single tool call the model makes with its arguments as it happens. The final answer prints separately at the end.

## Project layout

```
mcp_devos/
├── server.py              # MCP server: registers all tools, runs over stdio
├── security.py            # sandboxing / path validation — the security boundary
├── config.py              # sandbox root, file size limit, allowed extensions
├── tools/
│   ├── fs_tools.py          # list_directory, read_file
│   ├── git_tools.py         # git status / diff / log / last-commit-diff
│   └── log_tools.py         # read_log
├── client_test/
│   └── test_client.py       # Gemini client that connects to the server and runs the demo
├── demo/
│   └── buggy_app/           # sample app + log used by the debugging demo
├── tests/                   # automated tests for the security layer and all tools
├── requirements.txt
└── SAMPLE_OUTPUT.md          # a real captured test run and demo transcript
```

## Troubleshooting

**Model errors like "this model is no longer available to new users" or a 404 on the model name.** Gemini model availability changes by account and over time. If the hardcoded model name in [client_test/test_client.py](client_test/test_client.py) doesn't work for your key, list the models your key can actually use:

```python
from google import genai
client = genai.Client(api_key="your_key_here")
for m in client.models.list():
    if "generateContent" in (m.supported_actions or []):
        print(m.name)
```

Pick any current flash model from that list and update `MODEL_NAME` in [client_test/test_client.py](client_test/test_client.py).

**A `503 UNAVAILABLE` / "high demand" error.** This is Google's API being temporarily overloaded, not a bug in this project. Just retry.
