# Strawman Review -- EN-006 (Iteration 1)

**Reviewer:** critic-strawman (weakest link finder)
**Date:** 2026-02-12
**Workflow:** en006-20260212-001 (Platform Expansion - Schema Version Checking)
**Scope:** statusline.py, test_statusline.py, GETTING_STARTED.md

---

## Executive Summary

**Overall Score:** 0.88/1.00 (CONDITIONAL PASS with reservations)

**Verdict:** The implementation passes all 27 automated tests and meets functional requirements, but contains **5 critical weakest links** that pose maintenance burden, user confusion risk, and future extensibility concerns. The schema version checking works but uses a fragile integer-coercion approach that will break silently if future versions adopt semantic versioning. Documentation has a major discrepancy where it claims schema_version "cannot be overridden" but the code explicitly allows it.

**Primary Concerns:**
1. Integer-only schema versioning blocks future migration to semver
2. Config schema_version is user-overridable despite docs claiming otherwise
3. Warning output goes to stderr (not visible to users without debug mode)
4. Upgrade docs lack concrete migration examples
5. No validation that schema_version is a valid string before int coercion

---

## Scores by Dimension

| Dimension | Weight | Raw Score | Weighted | Notes |
|-----------|--------|-----------|----------|-------|
| **Correctness** | 0.25 | 0.96 | 0.240 | All tests pass; minor bug: config schema_version IS user-overridable despite docs |
| **Completeness** | 0.20 | 0.85 | 0.170 | Missing: semver support, migration script, schema changelog |
| **Robustness** | 0.25 | 0.84 | 0.210 | Weakest link: int() coercion fails silently for "1.0.0", "v1", etc. |
| **Maintainability** | 0.15 | 0.88 | 0.132 | Code is DRY but future schema changes require invasive edits |
| **Documentation** | 0.15 | 0.90 | 0.135 | Upgrade section exists but lacks migration examples |
| **TOTAL** | 1.00 | — | **0.887** | Below target (0.92) |

**Gate Status:** CONDITIONAL PASS (requires minor fixes to reach 0.92)

---

## Weakest Links (Ranked by Vulnerability)

### 1. INTEGER-ONLY SCHEMA VERSIONING (Robustness: CRITICAL)

**Location:** `statusline.py:186-196` (_schema_version_mismatch)

**Vulnerability:**
```python
def _schema_version_mismatch(found_version: Any) -> bool:
    expected = DEFAULT_CONFIG["schema_version"]
    try:
        return int(found_version) != int(expected)
    except (ValueError, TypeError):
        return True
```

**What Breaks First:**
- **Scenario:** Project adopts semantic versioning (e.g., "2.0.0" → "2.1.0")
- **Failure Mode:** `int("2.0.0")` raises ValueError → triggers version mismatch warning for EVERY invocation
- **User Impact:** All users with matching "2.0.0" config see spurious warnings
- **Extensibility:** Blocks migration to industry-standard semver without breaking change

**Evidence of Weakness:**
```python
# What happens when we upgrade to semver?
int("2.0.0")  # ValueError
int("v2")     # ValueError
int("2.1")    # ValueError (Python int() doesn't handle decimals)
```

**Why This is the Weakest Link:**
- NO escape hatch for future semver adoption
- Silent coercion failures (caught by except, interpreted as mismatch)
- Forces backward-incompatible change when industry moves to semver
- No test coverage for semver-like strings

**Recommendation:**
```python
def _schema_version_mismatch(found_version: Any, expected_version: Any) -> bool:
    """Compare schema versions with semver support."""
    # Try semantic versioning first
    if isinstance(found_version, str) and isinstance(expected_version, str):
        found_parts = found_version.lstrip("v").split(".")
        expected_parts = expected_version.lstrip("v").split(".")
        if all(p.isdigit() for p in found_parts) and all(p.isdigit() for p in expected_parts):
            # Compare major version only (breaking changes)
            return found_parts[0] != expected_parts[0]

    # Fallback to integer comparison
    try:
        return int(found_version) != int(expected_version)
    except (ValueError, TypeError):
        return True  # Unparseable = mismatch
```

---

### 2. CONFIG SCHEMA_VERSION IS USER-OVERRIDABLE (Correctness: HIGH)

**Location:** `statusline.py:219-221` (load_config)

**Vulnerability:**
```python
config = deep_merge(config, user_config)
# Restore schema_version from DEFAULT_CONFIG (not user-overridable)
config["schema_version"] = DEFAULT_CONFIG["schema_version"]
```

**Documentation Claims (GETTING_STARTED.md:1193):**
> The `schema_version` field is automatically managed by the script and **cannot be overridden** by user configuration.

**Actual Behavior:**
1. User config with `schema_version: "999"` is loaded
2. `deep_merge()` copies `"999"` into config
3. Line 221 overwrites it back to `"1"`
4. **BUT:** User's schema_version was ALREADY checked at line 210 before the merge!

**What's Technically Wrong:**
The docs say "cannot be overridden" but the code allows override temporarily (line 219) before restoring (line 221). This is confusing and violates least-surprise principle.

**Better Approach:**
```python
# Option 1: Strip schema_version before merge
user_config_safe = {k: v for k, v in user_config.items() if k != "schema_version"}
config = deep_merge(config, user_config_safe)

# Option 2: Update docs to say "ignored" not "cannot be overridden"
```

**Why This is a Weak Link:**
- Documentation inaccuracy erodes user trust
- Creates false sense of security ("I can't override it")
- Code behavior is technically correct but semantically confusing

---

### 3. VERSION MISMATCH WARNING INVISIBLE TO USERS (Robustness: HIGH)

**Location:** `statusline.py:213-218` (load_config)

**Vulnerability:**
```python
print(
    f"[ECW-WARNING] Config schema version mismatch: "
    f"found {user_schema_version}, "
    f"expected {DEFAULT_CONFIG['schema_version']}",
    file=sys.stderr,
)
```

**What Breaks First:**
- **Scenario:** User upgrades script, keeps old config file with schema_version: "0"
- **Failure Mode:** Warning goes to **stderr**, which Claude Code status hooks typically discard
- **User Impact:** User never sees the warning → continues using outdated config unknowingly
- **Requirements Gap:** Handoff doc says "version mismatch warning" but doesn't specify visibility requirement

**Test Weakness:**
`run_schema_version_mismatch_warning_test()` only checks that warning exists in stderr:
```python
combined_output = result.stdout + result.stderr
has_warning = "version" in combined_output.lower() and "mismatch" in combined_output.lower()
```

This test passes even if users NEVER see the warning in production (because stderr is hidden).

**Why This is the Weakest Link:**
- Warning exists but is **functionally invisible** to end users
- Test gives false confidence (tests stderr, users see stdout)
- Upgrade path relies on users seeing warnings they'll never see
- No mechanism to surface warnings to Claude Code UI

**Recommendation:**
```python
# Option 1: Add visual indicator to status line output
if version_mismatch_detected:
    status_line = f"⚠️ {status_line} (config outdated)"

# Option 2: Use debug_log (at least appears in ECW_DEBUG=1 mode)
debug_log(f"Config schema version mismatch: found {user_schema_version}, expected {expected}")

# Option 3: Document that warnings are debug-only
```

---

### 4. UPGRADE DOCS LACK MIGRATION EXAMPLES (Documentation: MEDIUM)

**Location:** GETTING_STARTED.md:1136-1211 (Upgrading section)

**Vulnerability:**
The "Config File Migration" section (lines 1167-1194) provides NO concrete migration steps for users with:
- Existing v1 configs that need schema_version added
- Configs from pre-EN-006 versions (no schema_version)
- Edge cases (corrupt state file, mismatched versions)

**What's Missing:**
```markdown
### Migration Example: Adding schema_version to Existing Config

**Before (pre-2.1.0 config):**
```json
{
  "cost": {
    "currency_symbol": "CAD "
  }
}
```

**After (recommended for 2.1.0+):**
```json
{
  "schema_version": "1",  // ADD THIS LINE
  "cost": {
    "currency_symbol": "CAD "
  }
}
```

**Note:** Adding schema_version is OPTIONAL. If omitted, the script assumes your config is compatible with the current version.
```

**Why This is a Weak Link:**
- Users don't know whether they SHOULD add schema_version
- No guidance on what to do if they see a mismatch warning
- "Forward-compatible" claim (line 1169) is vague without examples

**Actual User Questions:**
1. "My config has no schema_version. Do I need to add it?"
2. "I got a mismatch warning. What do I do?"
3. "When should I delete my state file?"

**None of these are answered.**

---

### 5. NO VALIDATION FOR SCHEMA_VERSION TYPE (Robustness: MEDIUM)

**Location:** `statusline.py:64` (DEFAULT_CONFIG), `statusline.py:340` (save_state)

**Vulnerability:**
```python
DEFAULT_CONFIG: Dict[str, Any] = {
    "schema_version": "1",  # String
    ...
}

# In save_state:
state["schema_version"] = DEFAULT_CONFIG["schema_version"]  # No type check
```

**What Breaks First:**
- **Scenario:** Developer accidentally changes DEFAULT_CONFIG["schema_version"] to integer 1
- **Failure Mode:** State file written with `"schema_version": 1` (JSON number, not string)
- **User Impact:** Next load fails comparison `int(1) != int("1")` → false mismatch
- **Detection:** NO validation that schema_version is a string before writing

**Missing Guard:**
```python
def save_state(config: Dict, state: Dict[str, Any]) -> None:
    # ... existing code ...
    schema_version = DEFAULT_CONFIG["schema_version"]
    if not isinstance(schema_version, str):
        raise TypeError(f"schema_version must be string, got {type(schema_version).__name__}")
    state["schema_version"] = schema_version
    # ... rest of function ...
```

**Why This is a Weak Link:**
- Silent type coercion can hide bugs
- No runtime validation of critical field
- JSON allows both `"1"` (string) and `1` (number) → subtle incompatibilities

---

## Findings

### Critical (C) - Blocks Future Requirements

#### C-01: Schema Version Strategy Locks Out Semver
- **Location:** `statusline.py:186-196`
- **Impact:** Prevents migration to semantic versioning (industry standard)
- **Risk:** Next major version (3.0.0) will break version checking entirely
- **Fix Effort:** 2 hours (implement semver parser + tests)
- **Priority:** HIGH (blocks extensibility goal)

---

### Major (M) - Reduces Effectiveness

#### M-01: Version Mismatch Warning Invisible to Users
- **Location:** `statusline.py:213-218`
- **Impact:** Users never see upgrade warnings → run with outdated configs
- **Risk:** Defeats purpose of version checking
- **Fix Effort:** 1 hour (add visual indicator or improve docs)
- **Priority:** HIGH (defeats feature purpose)

#### M-02: Config Documentation Inaccuracy
- **Location:** GETTING_STARTED.md:1193, statusline.py:219-221
- **Impact:** Documentation says "cannot be overridden" but code allows temporary override
- **Risk:** User confusion, trust erosion
- **Fix Effort:** 30 minutes (update docs or refactor merge logic)
- **Priority:** MEDIUM

---

### Minor (m) - Reduces Maintainability

#### m-01: Missing Migration Examples in Docs
- **Location:** GETTING_STARTED.md:1167-1194
- **Impact:** Users unsure whether to add schema_version to existing configs
- **Risk:** Support burden, uncertainty
- **Fix Effort:** 45 minutes (add concrete examples)
- **Priority:** MEDIUM

#### m-02: No Type Validation for schema_version
- **Location:** `statusline.py:64, 340`
- **Impact:** Accidental type changes cause silent failures
- **Risk:** Low (developer error, not user error)
- **Fix Effort:** 15 minutes (add isinstance check)
- **Priority:** LOW

---

## Recommendations

### Immediate (Required for 0.92 Gate)

1. **Fix Documentation Inaccuracy (M-02)**
   - Update GETTING_STARTED.md line 1193 to say "ignored" instead of "cannot be overridden"
   - OR refactor code to strip schema_version before deep_merge
   - **Effort:** 30 minutes
   - **Impact:** +0.02 on Documentation score → 0.92 weighted

2. **Add Migration Examples (m-01)**
   - Insert concrete before/after examples in GETTING_STARTED.md:1175
   - Address top-3 user questions (see Weakest Link #4)
   - **Effort:** 45 minutes
   - **Impact:** +0.03 on Documentation score → 0.95 weighted

### Short-Term (Next Iteration)

3. **Make Warnings Visible (M-01)**
   - Option A: Add visual indicator to status line when version mismatch detected
   - Option B: Document that warnings are debug-only + how to enable ECW_DEBUG
   - **Effort:** 1 hour
   - **Impact:** +0.05 on Robustness score

4. **Add Semver Support (C-01)**
   - Implement semver-aware comparison in _schema_version_mismatch
   - Add tests for "2.0.0", "v3", "1.2.3" formats
   - **Effort:** 2 hours
   - **Impact:** +0.10 on Robustness + Maintainability scores

### Long-Term (Future Proofing)

5. **Schema Migration Framework**
   - Add migration hooks for incompatible schema changes
   - Auto-migrate old state files on version bumps
   - Document schema changelog
   - **Effort:** 4 hours
   - **Impact:** +0.08 on Completeness + Maintainability scores

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Semver adoption breaks version check | HIGH | HIGH | Implement semver support now |
| Users never see version warnings | HIGH | MEDIUM | Add visual indicator or update docs |
| Config docs mislead users | MEDIUM | LOW | Fix "cannot be overridden" claim |
| Missing migration examples cause confusion | MEDIUM | LOW | Add concrete examples |
| Type error in schema_version | LOW | MEDIUM | Add isinstance validation |

---

## Test Coverage Gaps

1. **No test for semver-like strings** ("1.0.0", "v2", "2.1")
   - Current: Only tests integer-coercible strings ("1", "0.0.1" as float-like)
   - Gap: ValueError paths are tested but not documented

2. **No test for stdout visibility of warnings**
   - Current: Tests stderr for warning presence
   - Gap: Doesn't verify users WOULD see warnings in production

3. **No test for schema_version type safety**
   - Current: Assumes string, no validation
   - Gap: Integer schema_version in DEFAULT_CONFIG would pass tests but break comparisons

---

## Conclusion

The EN-006 implementation is **functionally correct** (27/27 tests pass) but suffers from **5 critical weakest links** that pose future risk:

1. **Integer-only versioning blocks semver** (most vulnerable)
2. **Config override behavior contradicts docs**
3. **Warnings invisible to users** (defeats feature purpose)
4. **Missing migration examples** (user confusion)
5. **No type validation** (silent failures)

**Verdict:** CONDITIONAL PASS at 0.887 score (target: 0.92)

**To Reach 0.92:**
- Fix documentation inaccuracy (+0.02)
- Add migration examples (+0.03)
- Total: 0.887 + 0.05 = **0.937** ✓

**Strawman Perspective:** The implementation WORKS but is FRAGILE. The weakest link (integer-only versioning) will cause a breaking change when the project inevitably adopts semantic versioning. Fix this NOW while the codebase is small.

---

**Signed:** critic-strawman (weakest link finder)
**Date:** 2026-02-12
**Status:** CONDITIONAL PASS with HIGH-priority recommendations
