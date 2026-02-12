# EN-006: Platform Expansion

> **Type:** enabler
> **Status:** pending
> **Priority:** low
> **Impact:** low
> **Enabler Type:** exploration
> **Created:** 2026-02-03T00:00:00Z
> **Due:** -
> **Completed:** -
> **Parent:** FEAT-003
> **Owner:** -
> **Effort:** 2h

---

## Summary

Improve upgrade experience and forward compatibility for the status line script.

**Technical Scope:**
- Upgrade path documentation (version migration instructions)
- Schema version checking (detect config/state format mismatches)

> **Note:** Hardware platform testing (ARM Linux, Windows ARM, FreeBSD) has been split out to [EN-009](../EN-009-hardware-platform-testing/EN-009-hardware-platform-testing.md) as it requires physical hardware access.

---

## Children (Tasks)

### Task Inventory

| ID | Title | Status | Effort |
|----|-------|--------|--------|
| TASK-001 | Add upgrade path documentation | pending | 1h |
| TASK-002 | Add schema version checking | pending | 1h |

---

## Acceptance Criteria

- [ ] Upgrade instructions in GETTING_STARTED.md
- [ ] Schema version field in config/state files
- [ ] Version mismatch detection with user-friendly warning
- [ ] Backward compatibility for unversioned configs

---

## Source Gaps

| Gap ID | Description |
|--------|-------------|
| G-022 | Upgrade path documentation |

---

## History

| Date | Author | Status | Notes |
|------|--------|--------|-------|
| 2026-02-03 | Claude | pending | Enabler created |
| 2026-02-12 | Claude | pending | Scope narrowed: hardware testing tasks (TASK-001/002/003) split to EN-009. Effort reduced 8h → 2h. Tasks renumbered. |

---
