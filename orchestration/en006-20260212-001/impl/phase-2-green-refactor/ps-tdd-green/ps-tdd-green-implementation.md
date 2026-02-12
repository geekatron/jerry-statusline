# ps-tdd-green Implementation Report

**Workflow:** en006-20260212-001
**Phase:** Phase 2 - GREEN (Make Failing Tests Pass)
**Agent:** ps-tdd-green
**Date:** 2026-02-12

---

## Summary

Implemented 2 tasks to make all 6 failing EN-006 RED tests pass:
- **TASK-001:** Added upgrade path documentation to GETTING_STARTED.md
- **TASK-002:** Added schema version checking to statusline.py

All 27 tests pass (22 existing + 5 previously failing + 1 already passing). Zero regressions.

---

## TASK-001: Upgrade Path Documentation

### File: `GETTING_STARTED.md`

**Changes:**

1. **Table of Contents** (line 24): Added entry `14. [Upgrading](#upgrading)`

2. **New "Upgrading" section** (inserted before "Next Steps"): Contains:
   - **Version History table** - maps schema versions to script versions with change descriptions (REQ-EN006-002)
   - **Upgrade Command** - single `curl` command for macOS/Linux, `Invoke-WebRequest` for Windows (REQ-EN006-006)
   - **Config File Migration** - before/after JSON examples showing optional `schema_version` field, explains forward-compatibility (REQ-EN006-003)
   - **State File Notes** - safe to delete, auto-recreated, version mismatch behavior (REQ-EN006-004)
   - **Breaking Change Checklist** - 4-step checklist for major version upgrades (REQ-EN006-005)

### Requirements Satisfied

| Requirement | Status |
|-------------|--------|
| REQ-EN006-001 | Done - Upgrade section in GETTING_STARTED.md, linked from TOC |
| REQ-EN006-002 | Done - Version history table |
| REQ-EN006-003 | Done - Config migration with before/after examples |
| REQ-EN006-004 | Done - State file compatibility notes |
| REQ-EN006-005 | Done - Breaking change checklist |
| REQ-EN006-006 | Done - Single-command upgrade instructions |

---

## TASK-002: Schema Version Checking

### File: `statusline.py`

**Change 1: Add `schema_version` to DEFAULT_CONFIG (lines 63-64)**
```python
DEFAULT_CONFIG: Dict[str, Any] = {
    # Schema version for config/state compatibility checking
    "schema_version": "1",
    # Display settings
    "display": {
```
Satisfies: REQ-EN006-010, REQ-EN006-012

**Change 2: Version check in `load_config()` (lines 195-213)**
- After loading user config JSON, checks `schema_version` field
- If user has a schema_version that doesn't match (integer comparison), prints warning to stderr
- Uses `int()` comparison with `ValueError`/`TypeError` catch for non-integer versions
- After `deep_merge()`, restores `schema_version` from `DEFAULT_CONFIG` (not user-overridable)
- Warning always goes to stderr (never stdout), visible without ECW_DEBUG

```python
user_schema_version = user_config.get("schema_version")
if user_schema_version is not None:
    expected = DEFAULT_CONFIG["schema_version"]
    mismatch = False
    try:
        mismatch = int(user_schema_version) != int(expected)
    except (ValueError, TypeError):
        mismatch = True
    if mismatch:
        print(
            f"[ECW-WARNING] Config schema version mismatch: "
            f"found {user_schema_version}, expected {expected}",
            file=sys.stderr,
        )
config = deep_merge(config, user_config)
config["schema_version"] = DEFAULT_CONFIG["schema_version"]
```
Satisfies: REQ-EN006-013, REQ-EN006-015, REQ-EN006-017, REQ-EN006-018

**Change 3: Version check in `load_state()` (lines 297-316)**
- After loading state JSON, checks `schema_version`
- If version mismatch, logs via `debug_log()` and returns defaults (fallback)
- If no version field (unversioned state), accepts silently

```python
loaded_version = loaded.get("schema_version")
expected_version = DEFAULT_CONFIG["schema_version"]
if loaded_version is not None:
    try:
        if int(loaded_version) != int(expected_version):
            debug_log(f"State schema version mismatch: ...")
            return default
    except (ValueError, TypeError):
        debug_log(f"State schema version mismatch: ...")
        return default
return loaded
```
Satisfies: REQ-EN006-014, REQ-EN006-016

**Change 4: Schema version in state file writes via `save_state()` (line 339)**
```python
state["schema_version"] = DEFAULT_CONFIG["schema_version"]
```
Satisfies: REQ-EN006-011

### Requirements Satisfied

| Requirement | Status |
|-------------|--------|
| REQ-EN006-010 | Done - `schema_version` in DEFAULT_CONFIG |
| REQ-EN006-011 | Done - `schema_version` in state file output |
| REQ-EN006-012 | Done - Simple integer string format ("1") |
| REQ-EN006-013 | Done - Unversioned config loads without error/warning |
| REQ-EN006-014 | Done - Unversioned state loads without error/warning |
| REQ-EN006-015 | Done - Version mismatch triggers warning (not rejection) |
| REQ-EN006-016 | Done - State version mismatch falls back to defaults |
| REQ-EN006-017 | Done - Warnings to stderr only (never stdout) |
| REQ-EN006-018 | Done - schema_version restored after deep_merge() |

---

## Test Results

```
RESULTS: 27 passed, 0 failed
```

All 27 tests pass:
- 22 existing tests: PASS (no regressions)
- 6 new EN-006 tests:
  - Schema Version in DEFAULT_CONFIG: PASS
  - Schema Version in State File: PASS
  - Schema Version Mismatch Warning: PASS
  - Unversioned Config Backward Compat: PASS
  - Schema Version Match No Warning: PASS
  - Upgrade Docs Exist in GETTING_STARTED.md: PASS

## Linting Results

```
$ uv run --with ruff ruff check statusline.py test_statusline.py
All checks passed!
```

---

## Design Notes

1. **Config version mismatch warning** uses `print(..., file=sys.stderr)` directly (not `debug_log()`) so the warning is always visible on stderr. This is because the test does not set `ECW_DEBUG=1` but expects to see the warning. The warning never appears on stdout, satisfying REQ-EN006-017's core constraint.

2. **State version mismatch** uses `debug_log()` for its warning since the test for state files does not check for stderr warnings -- it only checks that the state includes `schema_version`.

3. **Unversioned files** (no `schema_version` key) are accepted silently, providing full backward compatibility with pre-EN-006 configs and state files.

4. **Non-integer version strings** (e.g., "0.0.1") are caught by the `ValueError` handler and treated as a mismatch.
