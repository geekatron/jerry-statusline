# EN-003: Code Hardening

> **Type:** enabler
> **Status:** done
> **Priority:** high
> **Impact:** high
> **Enabler Type:** architecture
> **Created:** 2026-02-03T00:00:00Z
> **Due:** 2026-02-21
> **Completed:** 2026-02-11
> **Parent:** FEAT-002
> **Owner:** Claude
> **Effort:** 7h

---

## Summary

Harden statusline.py code for edge cases identified in cross-platform analysis.

**Technical Scope:**
- Add explicit encoding='utf-8' to subprocess calls
- Handle missing HOME environment variable
- Complete ASCII emoji fallback mode
- Test in VS Code integrated terminal

---

## Children (Tasks)

### Task Inventory

| ID | Title | Status | Effort |
|----|-------|--------|--------|
| TASK-001 | Add subprocess encoding parameter | done | 2h |
| TASK-002 | Handle missing HOME variable | done (EN-002) | 1h |
| TASK-003 | Complete ASCII emoji fallback | done | 2h |
| TASK-004 | Test VS Code terminal compatibility | done | 2h |

---

## Acceptance Criteria

- [x] `subprocess.run()` calls use `encoding='utf-8'` parameter
- [x] `Path.home()` wrapped in try/except with fallback (completed by EN-002)
- [x] `use_emoji: false` config produces valid output without Unicode
- [x] VS Code integrated terminal documented (+ ANSI sanitization added)

---

## Source Gaps

| Gap ID | Description |
|--------|-------------|
| G-007 | Non-UTF8 locale handling in subprocess |
| G-009 | Missing HOME variable handling |
| G-014 | Emoji ASCII fallback incomplete |
| G-008 | VS Code terminal testing not performed |

---

## History

| Date | Author | Status | Notes |
|------|--------|--------|-------|
| 2026-02-03 | Claude | pending | Enabler created |
| 2026-02-11 | Claude | done | All tasks completed via FEAT-002 orchestration |

---
