# Barrier 1 Handoff: nse → impl

**Workflow:** en005-20260211-001
**Direction:** NASA-SE Pipeline → Implementation Pipeline
**Purpose:** Provide requirements + risk findings for GREEN phase implementation
**Date:** 2026-02-11

---

## Summary

The NSE pipeline Phase 1 completed with 15 formal requirements (nse-requirements) and 10 implementation risks assessed (nse-risk). This handoff provides the GREEN phase (ps-tdd-green) with implementation guidance and risk mitigations to follow.

---

## Requirements Summary (15 total)

### Must-Have Requirements (for GREEN Phase)

| Req ID | Shall Statement | Task | Implementation Target |
|--------|----------------|------|----------------------|
| REQ-EN005-001 | NO_COLOR disables all ANSI output when present | TASK-001 | `ansi_color()`, `ansi_reset()` at lines 302-311 |
| REQ-EN005-002 | NO_COLOR takes precedence over use_color config | TASK-001 | Precedence: NO_COLOR > use_color |
| REQ-EN005-003 | NO_COLOR uses presence check (not truthiness) | TASK-001 | `os.environ.get("NO_COLOR") is not None` |
| REQ-EN005-004 | use_color config toggle, default true | TASK-006 | Add to `DEFAULT_CONFIG["display"]` at line 67 |
| REQ-EN005-005 | use_color=false disables ANSI codes | TASK-006 | Modify `ansi_color()`, `ansi_reset()` |
| REQ-EN005-006 | use_color independent of use_emoji | TASK-006 | Separate config paths |
| REQ-EN005-007 | Atomic state writes (temp + rename) | TASK-005 | Modify `save_state()` at line 277 |
| REQ-EN005-008 | Atomic write failure degrades gracefully | TASK-005 | Preserve existing OSError catch |
| REQ-EN005-009 | Preserve existing error handling contract | TASK-005 | Don't break read-only FS behavior |

### Should/May Requirements (Documentation)

| Req ID | Shall Statement | Task | Target |
|--------|----------------|------|--------|
| REQ-EN005-010 | git_timeout configurable via config | TASK-003 | Already exists, validate |
| REQ-EN005-011 | git_timeout documented | TASK-003 | GETTING_STARTED.md |
| REQ-EN005-012 | UNC path limitations documented | TASK-002 | GETTING_STARTED.md |
| REQ-EN005-013 | UNC path alternatives (mapped drives, WSL) | TASK-002 | GETTING_STARTED.md |
| REQ-EN005-014 | SSH terminal requirements documented | TASK-004 | GETTING_STARTED.md |
| REQ-EN005-015 | tmux configuration documented | TASK-004 | GETTING_STARTED.md |

---

## Risk Mitigations (Critical for GREEN Phase)

### Top 3 Risks to Address During Implementation

**1. RSK-EN005-003 (Score 12 YELLOW): os.replace() cross-platform behavior**
- **Mitigation:** Use `tempfile.NamedTemporaryFile(delete=False, dir=state_file.parent)`
- **Critical:** Close the temp file BEFORE calling `os.replace()` (Windows holds mandatory file locks)
- **Critical:** Use `dir=state_file.parent` to avoid cross-device rename failures
- **Pattern:**
  ```python
  import tempfile
  fd = tempfile.NamedTemporaryFile(mode='w', dir=state_file.parent,
                                    suffix='.tmp', delete=False)
  try:
      json.dump(state, fd)
      fd.close()  # MUST close before os.replace on Windows
      os.replace(fd.name, str(state_file))
  except OSError as e:
      debug_log(f"State save failed: {e}")
      # Clean up temp file on failure
      try:
          os.unlink(fd.name)
      except OSError:
          pass
  ```

**2. RSK-EN005-001 (Score 9 YELLOW): NO_COLOR + use_color interaction**
- **Mitigation:** Implement precedence check at the top of `ansi_color()` and `ansi_reset()`
- **Critical:** Use `os.environ.get("NO_COLOR") is not None` (presence check, NOT truthiness)
- **Pattern:**
  ```python
  def ansi_color(code: int, config: Dict = None) -> str:
      # NO_COLOR takes precedence (no-color.org standard)
      if os.environ.get("NO_COLOR") is not None:
          return "" if code != 0 else ""
      # Config use_color check
      if config and not safe_get(config, "display", "use_color", default=True):
          return "" if code != 0 else ""
      # Normal ANSI output
      if code == 0:
          return "\033[0m"
      return f"\033[38;5;{code}m"
  ```

**3. RSK-EN005-005 (Score 8 YELLOW): Test interference**
- **Mitigation:** Each test already uses subprocess isolation + finally cleanup
- **Verify:** NO_COLOR is explicitly removed from env when testing use_color alone
- **Verify:** Config file cleanup in every test's `finally` block

---

## Implementation Order (Recommended)

1. **Batch A first** (TASK-006 → TASK-001): Add use_color config, then NO_COLOR
2. **Batch B next** (TASK-005): Atomic writes (independent, can be done separately)
3. **Batch C last** (TASK-002 → TASK-003 → TASK-004): Documentation

---

## Artifact References

- **Requirements:** `orchestration/en005-20260211-001/nse/phase-1-requirements/nse-requirements/nse-requirements-analysis.md`
- **Risk Assessment:** `orchestration/en005-20260211-001/nse/phase-1-requirements/nse-risk/nse-risk-assessment.md`
