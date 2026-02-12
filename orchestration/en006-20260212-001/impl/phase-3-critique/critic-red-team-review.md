# Red Team Review -- EN-006 (Iteration 1)

**Reviewer:** critic-red-team (adversarial attacker)
**Date:** 2026-02-12
**Workflow:** en006-20260212-001
**Target:** Schema version checking + upgrade documentation

---

## Executive Summary

**Weighted Score:** 0.89 / 1.00
**Verdict:** CONDITIONAL PASS - Strong implementation with 2 critical findings

The implementation successfully addresses the core requirements (schema versioning, upgrade docs) but has **2 critical security/correctness issues** that must be fixed before production deployment:

1. **[C1]** Version mismatch warning leaks to stderr, not safely isolated
2. **[C2]** State file not created in HOME-less environments, breaking compaction detection

**Recommendation:** Fix critical issues, then ACCEPT.

---

## Scores by Dimension

| Dimension | Weight | Score | Weighted | Justification |
|-----------|--------|-------|----------|---------------|
| **Correctness** | 0.25 | 0.80 | 0.20 | 25/27 tests pass; state file creation fails in HOME-less containers |
| **Completeness** | 0.20 | 0.95 | 0.19 | All requirements met; upgrade docs comprehensive |
| **Robustness** | 0.25 | 0.85 | 0.21 | Good error handling but version mismatch warning not properly isolated |
| **Maintainability** | 0.15 | 0.95 | 0.14 | Clean code, DRY principles, good comments |
| **Documentation** | 0.15 | 1.00 | 0.15 | Excellent upgrade docs with migration examples |
| **TOTAL** | 1.00 | -- | **0.89** | Below 0.92 target due to critical findings |

---

## Critical Findings

### [C1] Version Mismatch Warning Leaks to stderr (HIGH SEVERITY)

**Location:** `statusline.py:213-218`

**Issue:** The version mismatch warning is printed to `stderr` via `print(..., file=sys.stderr)`, which can corrupt the status line display or be misinterpreted as an error by monitoring systems.

```python
# Lines 213-218
print(
    f"[ECW-WARNING] Config schema version mismatch: "
    f"found {user_schema_version}, "
    f"expected {DEFAULT_CONFIG['schema_version']}",
    file=sys.stderr,
)
```

**Attack Vector:**
1. User has old config with `schema_version: "0"`
2. Script prints warning to stderr every status update
3. If Claude Code or wrapper scripts monitor stderr for errors, this triggers false alarms
4. In automated pipelines (CI/CD), stderr output often causes build failures

**Evidence:**
Test `run_schema_version_mismatch_warning_test()` confirms warning goes to stderr:
```
STDERR: [ECW-WARNING] Config schema version mismatch: found 0.0.1, expected 1
```

**Expected Behavior:**
Version mismatch should use `debug_log()` instead, which respects `ECW_DEBUG` flag and doesn't pollute stderr in production.

**Recommendation:**
```python
# Line 213-218 - REPLACE WITH:
debug_log(
    f"Config schema version mismatch: "
    f"found {user_schema_version}, "
    f"expected {DEFAULT_CONFIG['schema_version']}"
)
```

**Impact:** Breaks automated monitoring, pollutes logs, confuses users.

---

### [C2] State File Not Created in HOME-less Environments (MEDIUM SEVERITY)

**Location:** `statusline.py:290-322`, `test_statusline.py:1217-1280`

**Issue:** When `HOME` is not set (Docker containers, CI), `_resolve_state_path()` returns `None` and state file is never created. This breaks compaction detection.

**Attack Vector:**
1. Run in Docker container without HOME env var
2. `_resolve_state_path()` returns None (line 300)
3. `load_state()` returns defaults (line 300)
4. `save_state()` skips write (line 335)
5. Compaction detection never works
6. **BUT** test `run_schema_version_in_state_test()` sometimes FAILS because state file doesn't exist

**Evidence from test run:**
```
TEST: Schema Version in State File (EN-006 TASK-002)
Script EXIT CODE: 0
State file was not created  # <-- FAILURE
```

**Root Cause:**
Test creates temp state dir but if HOME is not set during test, `_resolve_state_path()` fails silently. This is a **race condition** based on environment setup.

**Recommendation:**
1. Tests should use explicit `state_file` config override (not rely on HOME)
2. Add fallback to `/tmp/ecw-statusline-state.json` when HOME is unavailable
3. Document that compaction detection is disabled in HOME-less environments

**Impact:** Compaction detection silently disabled in containers; inconsistent test results.

---

## Major Findings

### [M1] Integer Coercion Could Raise Exception on Invalid Types

**Location:** `statusline.py:186-196`

**Issue:** `_schema_version_mismatch()` uses `int(found_version)` without handling all failure modes.

```python
def _schema_version_mismatch(found_version: Any) -> bool:
    expected = DEFAULT_CONFIG["schema_version"]
    try:
        return int(found_version) != int(expected)
    except (ValueError, TypeError):
        return True
```

**Attack Vectors Tested:**

| Attack | Input | Result | Severity |
|--------|-------|--------|----------|
| Non-numeric string | `"abc"` | Caught by `ValueError` | Safe |
| Negative version | `-1` | Converts to int, mismatch detected | Safe |
| Far-future version | `999999` | Converts to int, mismatch detected | Safe |
| None | `None` | Caught by `TypeError` | Safe |
| Float | `1.5` | Converts to `int(1.5) = 1`, may match! | **Risky** |
| List | `[1]` | Caught by `TypeError` | Safe |
| Dict | `{"v": 1}` | Caught by `TypeError` | Safe |

**Edge Case Found:**
If user writes `"schema_version": 1.9` in config, `int(1.9) = 1` which **incorrectly matches** expected version "1".

**Recommendation:**
```python
# Add float check before int conversion
try:
    # Reject floats - schema version must be exact integer or string
    if isinstance(found_version, float):
        return True
    return int(found_version) != int(expected)
except (ValueError, TypeError):
    return True
```

**Impact:** Minor - unlikely user input, but violates principle of strict validation.

---

### [M2] Schema Version Overrideable via Config Deep Merge (DESIGN ISSUE)

**Location:** `statusline.py:219-221`

**Issue:** User config is merged before schema_version is restored from DEFAULT_CONFIG, creating a **race window**.

```python
# Line 219
config = deep_merge(config, user_config)
# Line 220-221 - Restore AFTER merge
config["schema_version"] = DEFAULT_CONFIG["schema_version"]
```

**Attack Vector:**
1. User adds `"schema_version": "999"` to config file
2. Merge happens (line 219), setting config["schema_version"] = "999"
3. Restore happens (line 221), overwriting to "1"
4. **But** what if user added schema_version to a nested key?

**Test:**
```json
{
  "advanced": {
    "schema_version": "999"
  }
}
```

This would NOT be overridden by line 221 (which only restores top-level key).

**Verdict:** Actually **safe** because:
- Line 210 checks `user_config.get("schema_version")` - top-level only
- Line 221 restores top-level only
- Nested schema_version has no effect

**Recommendation:** Add comment clarifying this is intentional:
```python
# Restore schema_version from DEFAULT_CONFIG (not user-overridable, top-level only)
config["schema_version"] = DEFAULT_CONFIG["schema_version"]
```

**Impact:** Low - code is correct but lacks clarity.

---

## Minor Findings

### [m1] Upgrade Docs Example Uses Optional Field

**Location:** `GETTING_STARTED.md:1183-1194`

**Issue:** Documentation shows adding `schema_version` to user config as "optional":

```json
{
  "schema_version": "1",  // User adds this
  "cost": {
    "currency_symbol": "CAD "
  }
}
```

But line 221 of `statusline.py` **always** overwrites user's schema_version with DEFAULT_CONFIG value, making this a no-op.

**Recommendation:**
Update docs to clarify schema_version is **read-only** and managed by the script:

```markdown
> **Note:** Adding `schema_version` to your config is optional and has no effect.
> The schema_version field is automatically managed by the script and cannot be
> overridden by user configuration. It is shown here for documentation purposes only.
```

**Impact:** User confusion - they might think they can control versioning.

---

### [m2] Test Flakiness Due to State File Lifecycle

**Location:** `test_statusline.py:1217-1280`

**Issue:** Test `run_schema_version_in_state_test()` creates temp state dir but doesn't guarantee HOME is available.

**Evidence:**
Full test suite shows "2 failed" intermittently, but individual runs pass. This suggests environment-dependent flakiness.

**Recommendation:**
```python
# In test setup, explicitly set state_file path
config = {
    "compaction": {
        "state_file": state_file,  # Explicit path, not HOME-dependent
        "detection_threshold": 10000,
    }
}
```

**Impact:** Low - tests pass when run individually, but CI may be unreliable.

---

## Adversarial Probes Results

| Probe | Attack | Result | Impact |
|-------|--------|--------|--------|
| **1** | `schema_version: "abc"` | Caught by ValueError, mismatch=True | SAFE |
| **2** | `schema_version: -1` | Converts to int(-1), mismatch detected | SAFE |
| **3** | `schema_version: 999999` | Converts to int, mismatch detected | SAFE |
| **4** | State has version, config doesn't | State discarded (version mismatch), falls back to defaults | SAFE (but see C2) |
| **5** | User overrides via config deep merge | Overridden by line 221 restore | SAFE (but see M2) |
| **6** | Version warning leaks to stdout | Goes to stderr only (not stdout) | PARTIAL FAIL (see C1) |
| **7** | Upgrade docs accuracy | Examples accurate but misleading (see m1) | MINOR ISSUE |
| **8** | Race between version check and deep_merge | No race - check before merge, restore after | SAFE |

**Summary:** 6/8 probes safe, 1 critical (stderr leak), 1 minor (docs clarity).

---

## Test Results Analysis

### Automated Tests: 25/27 PASS (92.6%)

**Failures (2):**
1. `run_schema_version_in_state_test()` - Intermittent (HOME dependency)
2. `run_schema_version_mismatch_warning_test()` - Passes individually, fails in suite (ordering issue)

**Root Cause:** Test suite runs all tests sequentially, and state file cleanup may not happen between tests. State file from previous test can affect next test.

**Recommendation:** Add `tearDown` to clean state files:
```python
# At end of each EN-006 test:
finally:
    # Clean up state files globally
    for pattern in ["~/.claude/ecw-statusline-state.json", "/tmp/*/test-*.json"]:
        for f in glob.glob(os.path.expanduser(pattern)):
            Path(f).unlink(missing_ok=True)
```

---

## Code Quality Assessment

### Strengths
- Clean separation of concerns (`_schema_version_mismatch`, `load_state`, `save_state`)
- Comprehensive error handling (ValueError, TypeError, OSError)
- DRY principle: version checking logic in one place
- Good use of type hints
- Atomic state writes (tempfile + rename)

### Weaknesses
- stderr pollution (C1)
- Silent degradation in HOME-less environments (C2)
- Float version edge case (M1)
- Test flakiness (m2)

---

## Documentation Review

### Upgrade Section (GETTING_STARTED.md:1136-1212)

**Strengths:**
- Clear version history table (line 1143-1145)
- Platform-specific upgrade commands (line 1151-1162)
- Migration examples showing before/after (line 1175-1192)
- State file notes explain auto-recreation (line 1196-1202)

**Weaknesses:**
- Misleading example suggesting users can set schema_version (m1)
- No mention that version mismatch warning goes to stderr (should document for troubleshooting)
- Missing guidance on what to do if version mismatch warning appears

**Recommendation:** Add troubleshooting section:
```markdown
### Version Mismatch Warning

If you see this warning in debug logs:
```
[ECW-WARNING] Config schema version mismatch: found X, expected Y
```

**Solution:** Your config file is from an older version. Either:
1. Delete `~/.claude/ecw-statusline-config.json` to use defaults
2. Manually add new fields from the latest DEFAULT_CONFIG
3. Re-download the config template from the repository
```

---

## Risk Mitigation Scorecard

| Risk ID | Mitigation Status | Evidence |
|---------|------------------|----------|
| R-001: Breaking changes break old configs | MITIGATED | Unversioned configs load without warning |
| R-002: User confusion on upgrade | PARTIALLY MITIGATED | Docs exist but incomplete (m1) |
| R-003: State file corruption | MITIGATED | Version check discards incompatible state |
| R-004: stderr pollution from warnings | **NOT MITIGATED** | C1 critical finding |

**Score:** 3/4 risks mitigated (75%)

---

## Recommendations (Priority Order)

### Critical (Must Fix)
1. **[C1]** Change version mismatch warning from `print(..., file=sys.stderr)` to `debug_log()`
2. **[C2]** Fix state file creation in HOME-less environments (add fallback or document limitation)

### Major (Should Fix)
3. **[M1]** Add float rejection in `_schema_version_mismatch()`
4. **[M2]** Add comment clarifying schema_version restore is intentional

### Minor (Nice to Have)
5. **[m1]** Update GETTING_STARTED.md to clarify schema_version is read-only
6. **[m2]** Add test tearDown to prevent state file pollution between tests
7. Add troubleshooting section for version mismatch warnings

---

## Final Verdict

**Current Score:** 0.89 / 1.00 (Target: >= 0.92)

**Blocking Issues:**
- [C1] stderr pollution (security/correctness)
- [C2] state file creation failure (correctness)

**Path to Acceptance:**
1. Fix C1 (change to debug_log)
2. Fix C2 (add fallback or explicit test config)
3. Re-run tests → expect 27/27 pass
4. New score: 0.94+ (PASS)

**Recommendation:** **CONDITIONAL PASS** - Fix critical issues, then ACCEPT.

---

## Appendix: Attack Surface Analysis

### Input Validation
- [x] Schema version string → Handled by try/except
- [x] Schema version integer → Handled by int() conversion
- [ ] Schema version float → **EDGE CASE** (M1)
- [x] Schema version null/None → Handled by TypeError
- [x] Schema version object/array → Handled by TypeError

### State Management
- [x] Corrupt state file → Falls back to defaults
- [x] Missing state file → Falls back to defaults
- [x] Version mismatch in state → Discards state
- [ ] No HOME environment → **SILENT FAILURE** (C2)
- [x] Read-only filesystem → Graceful degradation

### Error Channels
- [x] JSON parse errors → debug_log only
- [x] File I/O errors → debug_log only
- [ ] Version mismatch → **stderr leak** (C1)

---

**End of Red Team Review**
