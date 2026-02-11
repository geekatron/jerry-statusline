# BUG-002: os.rmdir Fails on Windows Temp Dir Cleanup

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

`test_statusline.py` crashes on Windows with `OSError: [WinError 145] The directory is not empty` during temp directory cleanup in `run_readonly_state_test()`.

---

## Bug Details

### Error

```
File "test_statusline.py", line 687, in run_readonly_state_test
OSError: [WinError 145] The directory is not empty: 'C:\\Users\\RUNNER~1\\AppData\\Local\\Temp\\tmpyc_g54t9'
```

### Root Cause

`run_readonly_state_test()` creates a temp directory with `tempfile.mkdtemp()`, makes it read-only, runs a test, restores permissions, then attempts `os.rmdir()`. On Windows, the directory may contain residual files (e.g., from the subprocess or OS), making `os.rmdir()` fail since it only removes empty directories.

### Environment

- **Platform:** Windows Server 2025 (windows-latest)
- **Python:** 3.9, 3.10, 3.11, 3.12 (all affected)
- **Test:** `run_readonly_state_test()` (test 15 of 17)

### Fix

Replace `os.rmdir(readonly_dir)` with `shutil.rmtree(readonly_dir, ignore_errors=True)` which recursively removes the directory and handles Windows edge cases. The `shutil` import is already available in the test file.

---

## Tasks

| ID | Title | Status |
|----|-------|--------|
| T-001 | Replace os.rmdir with shutil.rmtree in test cleanup | done |

---

## History

| Date | Author | Status | Notes |
|------|--------|--------|-------|
| 2026-02-11 | Claude | in_progress | Bug identified from CI run 21912030014 |
| 2026-02-11 | Claude | done | Fixed: replaced os.rmdir() with shutil.rmtree(ignore_errors=True), added import shutil |

---
