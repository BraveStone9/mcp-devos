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

The model was given no other information, no file contents, and no hint about where the bug was. Everything below came from it autonomously calling tools exposed by [server.py](server.py), in this exact order:

```
CALLED: list_dir {}
CALLED: list_dir {'path': 'buggy_app'}
CALLED: read_log_file {'filename': 'buggy_app/app.log', 'lines': 100}
CALLED: read_source_file {'filepath': 'buggy_app/inventory.py'}
```

It first listed the project root, then the `buggy_app/` subfolder it found, then read the log file, then read the source file the log pointed to. Each step was chosen based on what the previous tool call returned.

Final response from the model:

```
I have investigated the inventory app (buggy_app/inventory.py and its log buggy_app/app.log).

### What is broken:
The application crashes with an IndexError: list index out of range when attempting
to apply a discount to an item price in apply_discount.

### Why it's happening:
1. In main(), the prices list contains 2 elements: [10, 20], which means valid
   0-based indices are 0 (for 10) and 1 (for 20).
2. The code calls apply_discount(prices, 2), passing 2 as the discount_index.
3. Inside apply_discount, it attempts to access prices[2]. Since index 2 is out of
   bounds for a list of length 2, Python raises an IndexError.
```

This matches the actual bug planted in [demo/buggy_app/inventory.py](demo/buggy_app/inventory.py) and the actual traceback in [demo/buggy_app/app.log](demo/buggy_app/app.log) — the model found and explained it correctly on its own.
