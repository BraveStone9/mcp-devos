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

The model was given no other information, no file contents, and no hint about where the bug was. [server.py](server.py) and [client_test/test_client.py](client_test/test_client.py) both log every step live, so this is the actual terminal output of one run, unedited apart from trimming the final answer:

```
22:49:25 [client] Launching MCP server: server.py
22:49:25 [client] Connected to server. Initializing MCP session...
22:49:26 [server] Starting DevOS MCP server (sandbox root: .../mcp_devos/demo)
22:49:26 [client] Session ready. Available tools: list_dir, read_source_file, git_status, git_diff, git_log, git_last_commit_diff, read_log_file
22:49:26 [client] Sending prompt to gemini-3.5-flash-lite: "Something is wrong with the inventory app. Can you investigate and tell me what's broken and why?"
22:49:28 [server] -> list_dir(path='.')
22:49:28 [server] <- list_dir ok
22:49:29 [server] -> list_dir(path='buggy_app')
22:49:29 [server] <- list_dir ok
22:49:29 [server] -> read_log_file(filename='buggy_app/app.log', lines=100, level_filter=None)
22:49:29 [server] <- read_log_file ok
22:49:30 [server] -> read_source_file(filepath='buggy_app/inventory.py')
22:49:30 [server] <- read_source_file ok
22:49:32 [client] Received final response from the model.
```

It first listed the project root, then the `buggy_app/` subfolder it found, then read the log file, then read the source file the log pointed to — each step chosen based on what the previous tool call returned, not a fixed script.

Final response from the model:

```
I have investigated the inventory app (buggy_app/inventory.py and its log file buggy_app/app.log). Here is what is broken and why:

### What is broken?
The application crashes with an IndexError: list index out of range inside the
apply_discount function when trying to calculate and print a discounted price in main().

### Why is it happening?
1. In main(), a list named prices is defined with two elements: [10, 20]. In Python,
   lists use 0-based indexing, meaning valid indices for this list are 0 (for 10)
   and 1 (for 20).
2. The code then calls apply_discount(prices, 2), passing 2 as the discount_index.
3. Inside apply_discount, the code attempts to access prices[discount_index]
   (which evaluates to prices[2]).
4. Since index 2 does not exist in a 2-element list, Python raises an IndexError.
```

This matches the actual bug planted in [demo/buggy_app/inventory.py](demo/buggy_app/inventory.py) and the actual traceback in [demo/buggy_app/app.log](demo/buggy_app/app.log) — the model found and explained it correctly on its own.
