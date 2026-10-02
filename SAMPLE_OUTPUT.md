# Sample Run

This is a real captured run of this project, included so anyone can see what it actually produces without having to set it up themselves.

## Test suite

Command: `pytest -v`, run against [tests/](tests/) (`test_security.py`, `test_fs_tools.py`, `test_git_tools.py`, `test_log_tools.py`).

```
38 passed, 1 skipped in 2.89s
```

The one skip is a symlink-escape test in [tests/test_security.py](tests/test_security.py) that only runs on systems where the current user has permission to create symlinks (commonly blocked by default on Windows).

## Debugging demo

Command: `python client_test/test_client.py`, running [client_test/test_client.py](client_test/test_client.py).

Prompt sent to the model:

```
Something is wrong with the inventory app. Can you investigate and tell me what's broken and why?
```

The model was given no other information, no file contents, and no hint about where the bug was. [server.py](server.py) and [client_test/test_client.py](client_test/test_client.py) both log every step live, and every run also saves that same log to a file. The raw, unedited log file from this exact run is [logs/sample_run.log](logs/sample_run.log):

```
23:09:01 [client] Launching MCP server: server.py
23:09:01 [client] Connected to server. Initializing MCP session...
23:09:03 [server] Starting DevOS MCP server (sandbox root: .../mcp_devos/demo)
23:09:03 [client] Session ready. Available tools: list_dir, read_source_file, git_status, git_diff, git_log, git_last_commit_diff, read_log_file
23:09:03 [client] Sending prompt to gemini-3.5-flash-lite: "Something is wrong with the inventory app. Can you investigate and tell me what's broken and why?"
23:09:04 [server] -> list_dir(path='.')
23:09:04 [server] <- list_dir ok
23:09:05 [server] -> list_dir(path='buggy_app')
23:09:05 [server] <- list_dir ok
23:09:26 [server] -> read_log_file(filename='buggy_app/app.log', lines=100, level_filter=None)
23:09:26 [server] <- read_log_file ok
23:09:27 [server] -> read_source_file(filepath='buggy_app/inventory.py')
23:09:27 [server] <- read_source_file ok
23:09:28 [client] Received final response from the model.
```

It first listed the project root, then the `buggy_app/` subfolder it found, then read the log file, then read the source file the log pointed to — each step chosen based on what the previous tool call returned, not a fixed script. (The 21-second gap before `read_log_file` is Gemini API latency, not this project — see the Troubleshooting section in the README if a run hangs much longer than that.)

Final response from the model:

```
I have investigated the inventory app (buggy_app/inventory.py and buggy_app/app.log) and found the root cause of the error.

### What is broken:
The inventory application crashes with an IndexError: list index out of range when
attempting to apply a discount to an item list.

### Why it is broken:
1. In main(), a list of prices is defined with two elements: prices = [10, 20]. In
   Python, lists use 0-based indexing, meaning valid indices for this list are 0 and 1.
2. The code then calls apply_discount(prices, 2), passing 2 as the discount_index.
3. Inside apply_discount, it attempts to access prices[2], which does not exist
   because index 2 points to a third element that is out of bounds for a 2-element list.
```

This matches the actual bug planted in [demo/buggy_app/inventory.py](demo/buggy_app/inventory.py) and the actual traceback in [demo/buggy_app/app.log](demo/buggy_app/app.log) — the model found and explained it correctly on its own.
