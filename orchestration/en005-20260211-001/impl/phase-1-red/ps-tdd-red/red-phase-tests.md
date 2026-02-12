# RED Phase Tests -- EN-005 Batch A (Color/ANSI Control)

**Workflow:** en005-20260211-001
**Agent:** ps-tdd-red
**Phase:** RED (failing tests written, implementation pending)
**Date:** 2026-02-11

---

## L0: Executive Summary

Three failing tests were added to `test_statusline.py` to validate ANSI color control behavior that does not yet exist in `statusline.py`. The tests cover the `NO_COLOR` environment variable (spec: no-color.org), a new `display.use_color` config toggle, and the full 4-scenario interaction matrix between these two controls. All 3 new tests FAIL as expected (RED state). All 17 existing tests continue to PASS.

---

## L1: Technical Details

### Tests Added

| # | Function Name | Lines | What It Validates |
|---|---|---|---|
| 1 | `run_no_color_env_test()` | 804-855 | When `NO_COLOR=1` is set in the environment, the script's stdout must contain ZERO ANSI escape sequences (regex: `\x1b\[[0-9;]*[a-zA-Z]`) while still producing valid output. |
| 2 | `run_use_color_disabled_test()` | 858-919 | When config `{"display": {"use_color": false}}` is written to `ecw-statusline-config.json` (with `NO_COLOR` explicitly unset), stdout must contain ZERO ANSI escape sequences. |
| 3 | `run_color_matrix_test()` | 922-1018 | Tests all 4 combinations of `use_color` (true/false) x `NO_COLOR` (set/unset). Expected: ANSI present ONLY when `use_color=true` AND `NO_COLOR` is unset. All other combinations must suppress ANSI. |

### Registration

All 3 tests are registered in `main()` at lines 1120-1138 under the comment block `# EN-005: Edge Case Handling - Batch A (Color/ANSI Control)`.

### Detection Pattern

All tests use the same ANSI detection regex from `statusline.py`:
```python
ansi_re = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")
```

The `re` module import was added to the test file's import block.

### Expected Failure Reasons

| Test | Why It Fails |
|---|---|
| `run_no_color_env_test` | `statusline.py` does not check `os.environ.get("NO_COLOR")` anywhere. `ansi_color()` and `ansi_reset()` unconditionally emit escape sequences. |
| `run_use_color_disabled_test` | `DEFAULT_CONFIG["display"]` has no `use_color` key. Even if set in the config file, nothing reads or acts on it. |
| `run_color_matrix_test` | Scenarios 2, 3, and 4 fail for the same reasons above. Scenario 1 (use_color=true, NO_COLOR unset) passes because ANSI is always emitted regardless. |

---

## L2: Traceability

| Test | TASK | Gap ID | Risk ID | Requirement |
|---|---|---|---|---|
| `run_no_color_env_test` | TASK-001 | G-016 | RSK-XPLAT-012 | NO_COLOR env var must disable all ANSI escape codes per no-color.org spec |
| `run_use_color_disabled_test` | TASK-006 | G-021 | RSK-XPLAT-012 | `display.use_color` config toggle must control ANSI output |
| `run_color_matrix_test` | TASK-001 + TASK-006 | G-016, G-021 | RSK-XPLAT-012 | Integration: NO_COLOR takes precedence over use_color config |

### Gap References

- **G-016**: No support for `NO_COLOR` environment variable (https://no-color.org/)
- **G-021**: No `display.use_color` config option to programmatically disable color output

### Risk Reference

- **RSK-XPLAT-012**: Terminal compatibility -- ANSI escape codes leak into output in environments that do not support them (pipes, CI logs, accessibility tools, NO_COLOR-compliant workflows)

---

## Test Run Results (Actual Output)

```
============================================================
TEST: NO_COLOR Environment Variable (G-016)
============================================================
STDOUT: [38;5;141m...Sonnet[0m[38;5;240m | [0m...
EXIT CODE: 0
FAIL: Found 28 ANSI escape sequences in output
  Sequences: ['\x1b[38;5;141m', '\x1b[0m', '\x1b[38;5;240m', '\x1b[0m', '\x1b[38;5;82m']...
Has output: True
No ANSI codes (expected): False

============================================================
TEST: use_color Config Disabled (G-021)
============================================================
STDOUT: [38;5;141m...Sonnet[0m[38;5;240m | [0m...
EXIT CODE: 0
FAIL: Found 28 ANSI escape sequences in output
  Sequences: ['\x1b[38;5;141m', '\x1b[0m', '\x1b[38;5;240m', '\x1b[0m', '\x1b[38;5;82m']...
Has output: True
No ANSI codes (expected): False

============================================================
TEST: Color Control Matrix (NO_COLOR x use_color)
============================================================

  Scenario: use_color=true, NO_COLOR unset
    Expected ANSI: YES | Found ANSI: True | PASS

  Scenario: use_color=true, NO_COLOR=1
    Expected ANSI: NO  | Found ANSI: True | FAIL
    ANSI sequences found: ['\x1b[38;5;141m', '\x1b[0m', '\x1b[38;5;240m']

  Scenario: use_color=false, NO_COLOR unset
    Expected ANSI: NO  | Found ANSI: True | FAIL
    ANSI sequences found: ['\x1b[38;5;141m', '\x1b[0m', '\x1b[38;5;240m']

  Scenario: use_color=false, NO_COLOR=1
    Expected ANSI: NO  | Found ANSI: True | FAIL
    ANSI sequences found: ['\x1b[38;5;141m', '\x1b[0m', '\x1b[38;5;240m']

  Matrix result: SOME FAILED

============================================================
RESULTS: 17 passed, 3 failed
============================================================
```

### Summary

- **Existing tests (17):** ALL PASS -- no regressions
- **New tests (3):** ALL FAIL -- confirmed RED state
- **Exit code:** 1 (as expected for failing tests)

---

## Files Modified

| File | Change |
|---|---|
| `test_statusline.py` | Added `import re`; added 3 test functions (`run_no_color_env_test`, `run_use_color_disabled_test`, `run_color_matrix_test`); registered them in `main()` |
| `red-phase-tests.md` | This documentation artifact (created) |
