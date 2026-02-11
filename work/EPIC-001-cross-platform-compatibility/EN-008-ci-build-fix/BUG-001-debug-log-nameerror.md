# BUG-001: debug_log NameError on Windows CI

> **Type:** bug
> **Status:** done
> **Priority:** critical
> **Impact:** high
> **Created:** 2026-02-11T16:00:00Z
> **Due:** 2026-02-11
> **Completed:** 2026-02-11T16:30:00Z
> **Parent:** [EN-008](EN-008-ci-build-fix.md)
> **Owner:** Claude
> **Effort:** 0.25h

---

## Summary

`statusline.py` crashes on Windows CI with `NameError: name 'debug_log' is not defined` when `Path.home()` raises `RuntimeError` in the `_get_config_paths()` function.

---

## Bug Details

### Error

```
File "statusline.py", line 172, in <module>
    CONFIG_PATHS = _get_config_paths()
  File "statusline.py", line 168, in _get_config_paths
    debug_log("HOME not available, skipping ~/.claude config path")
NameError: name 'debug_log' is not defined
```

### Root Cause

`_get_config_paths()` is called at module level (line 176: `CONFIG_PATHS = _get_config_paths()`). When `Path.home()` raises `RuntimeError` on Windows CI (HOME env var not set), the except block at line 172 calls `debug_log()`, which is defined at line 219 - later in the file. At module-init time, `debug_log` hasn't been defined yet.

### Environment

- **Platform:** Windows Server 2025 (windows-latest)
- **Python:** 3.9, 3.10, 3.11, 3.12 (all affected)
- **Trigger:** HOME environment variable not set in CI runner

### Fix

Remove the `debug_log()` call from `_get_config_paths()` since it runs before `debug_log` is defined. Use `pass` in the except block instead.

---

## Tasks

| ID | Title | Status |
|----|-------|--------|
| T-001 | Remove debug_log call from _get_config_paths except block | done |

---

## History

| Date | Author | Status | Notes |
|------|--------|--------|-------|
| 2026-02-11 | Claude | in_progress | Bug identified from CI run 21912030014 |
| 2026-02-11 | Claude | done | Fixed: replaced debug_log() call with pass in except block |

---
