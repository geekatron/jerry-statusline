# EN-003: Code Hardening

> **Type:** enabler
> **Status:** pending
> **Priority:** high
> **Impact:** high
> **Enabler Type:** architecture
> **Created:** 2026-02-03T00:00:00Z
> **Due:** 2026-02-21
> **Completed:** -
> **Parent:** FEAT-002
> **Owner:** -
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
| TASK-001 | Add subprocess encoding parameter | pending | 2h |
| TASK-002 | Handle missing HOME variable | pending | 1h |
| TASK-003 | Complete ASCII emoji fallback | pending | 2h |
| TASK-004 | Test VS Code terminal compatibility | pending | 2h |

---

## Acceptance Criteria

- [ ] `subprocess.run()` calls use `encoding='utf-8'` parameter
- [ ] `Path.home()` wrapped in try/except with fallback
- [ ] `use_emoji: false` config produces valid output without Unicode
- [ ] VS Code integrated terminal displays correctly

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

---
