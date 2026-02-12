# Barrier 1 Handoff: nse → impl

**Workflow:** en006-20260212-001
**Direction:** NASA-SE Pipeline → Implementation Pipeline
**Date:** 2026-02-12
**Phase Completed:** Phase 1 (Requirements + Risk)

---

## Requirements Summary (24 requirements)

### TASK-001: Upgrade Path Documentation (6 requirements)

| ID | Requirement | Priority |
|----|-------------|----------|
| REQ-EN006-001 | Upgrade section in GETTING_STARTED.md linked from TOC | Must |
| REQ-EN006-002 | Version history table showing changes per release | Must |
| REQ-EN006-003 | Config file migration guidance with before/after examples | Must |
| REQ-EN006-004 | State file compatibility notes (safe to delete, auto-recreated) | Must |
| REQ-EN006-005 | Breaking change checklist for major versions | Should |
| REQ-EN006-006 | Single-command upgrade instruction (`cp` or download) | Must |

### TASK-002: Schema Version Checking (9 requirements)

| ID | Requirement | Priority |
|----|-------------|----------|
| REQ-EN006-010 | `schema_version` field in DEFAULT_CONFIG | Must |
| REQ-EN006-011 | `schema_version` field in state file output | Must |
| REQ-EN006-012 | Version format: simple integer string ("1", "2") | Must |
| REQ-EN006-013 | Unversioned config loads without error or warning | Must |
| REQ-EN006-014 | Unversioned state loads without error or warning | Must |
| REQ-EN006-015 | Version mismatch triggers warning (not rejection) | Must |
| REQ-EN006-016 | State version mismatch: fall back to defaults | Should |
| REQ-EN006-017 | Warnings via debug_log() only (never pollute stdout) | Must |
| REQ-EN006-018 | Schema version not user-overridable (restored after deep_merge) | Must |

### Key Design Decisions

1. **Simple integer version** (not semver) - appropriate for single-file scope
2. **Warnings debug-only** - via `debug_log()` to stderr, never stdout
3. **Schema version restored after merge** - prevents user overriding in config file
4. **State reset on mismatch** - fall back to defaults rather than interpreting incompatible data

---

## Risk Summary (14 risks, top 4)

| ID | Risk | Score | Mitigation |
|----|------|-------|------------|
| RISK-EN006-004 | Version mismatch warning repeating every invocation | 9 (YELLOW) | Warn once via debug_log, suppress in normal mode |
| RISK-EN006-006 | Config loading path conflict breaking all users | 9 (YELLOW) | Advisory-only checking, never reject config |
| RISK-EN006-012 | Existing tests not covering version checking | 9 (YELLOW) | RED phase tests already written (5 tests) |
| RISK-EN006-001 | Version comparison edge cases | 6 (YELLOW) | Simple integer comparison, no semver needed |

### Top 3 Mitigations with Code-Level Guidance

**1. Advisory-only version checking:**
- Never reject a config or state file based on version
- Use `debug_log()` for warnings, never print to stdout
- Pattern: `if version != expected: debug_log(f"Config version {version} != expected {expected}")`

**2. Additive-only state file changes:**
- Use merge pattern: `{**default_state, **loaded_state}`
- Always write back all fields including new `schema_version`
- Old versions will silently pass through unknown fields

**3. Simple integer version comparison:**
- Use `int(loaded_version) != int(expected_version)` comparison
- No semver parsing needed (scope is single-file, not library)
- Catch `ValueError` for non-integer versions, treat as mismatch

### Recommended Implementation Order

1. TASK-001 (docs) first - zero regression risk
2. TASK-002 (code) in sub-steps:
   a. Add `schema_version` to DEFAULT_CONFIG
   b. Add `schema_version` to state file writes
   c. Add version check in `load_config()`
   d. Add version check in `load_state()`
   e. Restore `schema_version` after `deep_merge()`
   f. Run all tests (existing + new)

---

*Handoff artifact for ps-tdd-green implementation phase.*
