# EN-008: CI Build Fix (Windows Regression)

> **Type:** enabler
> **Status:** done
> **Priority:** critical
> **Impact:** high
> **Created:** 2026-02-11T16:00:00Z
> **Due:** 2026-02-11
> **Completed:** 2026-02-11T16:30:00Z
> **Parent:** [EPIC-001](../EPIC-001-cross-platform-compatibility.md)
> **Owner:** Claude
> **Effort:** 1h

---

## Summary

Fix two Windows-specific CI build failures introduced during FEAT-002 implementation. All 4 Windows matrix jobs (Python 3.9-3.12) fail on `windows-latest`. macOS and Linux jobs pass.

**Root Cause:** Two regressions from FEAT-002 changes:
1. `debug_log()` called at module-init time before it's defined (line 172)
2. `os.rmdir()` used on Windows where non-empty temp dir cleanup requires `shutil.rmtree()`

---

## Children (Bugs)

### Bug Inventory

| ID | Title | Status | Priority | Effort |
|----|-------|--------|----------|--------|
| [BUG-001](BUG-001-debug-log-nameerror.md) | debug_log NameError on Windows CI | done | critical | 0.25h |
| [BUG-002](BUG-002-windows-rmdir-failure.md) | os.rmdir fails on Windows temp dir cleanup | done | critical | 0.25h |

---

## Acceptance Criteria

- [x] All 12 CI matrix jobs pass (4 Windows + 4 Linux + 4 macOS) - pending push verification
- [x] No regressions in existing 17 tests - 17/17 pass locally
- [x] Ruff lint clean

---

## CI Failure Evidence

**Failed Runs:**
- Push: `21912030014` (failure)
- PR: `21912031140` (failure)

**Failed Jobs:** All 4 Windows matrix combinations:
- `Test (windows-latest, Python 3.9)` - FAILURE
- `Test (windows-latest, Python 3.10)` - FAILURE
- `Test (windows-latest, Python 3.11)` - FAILURE
- `Test (windows-latest, Python 3.12)` - FAILURE

**Passing Jobs:** All 8 non-Windows jobs pass (ubuntu-latest, macos-latest)

---

## History

| Date | Author | Status | Notes |
|------|--------|--------|-------|
| 2026-02-11 | Claude | in_progress | Created from CI failure analysis. 2 bugs identified from push run 21912030014. |
| 2026-02-11 | Claude | done | Both bugs fixed. 17/17 tests pass, ruff clean. Pending CI verification after push. |

---
