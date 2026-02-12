# EN-006 Risk Assessment

**Work Item:** EN-006 (Platform Expansion)
**Assessment Date:** 2026-02-12
**Assessor:** nse-risk agent (EN-006 orchestration)
**Methodology:** NASA NPR 7123.1D / NPR 8000.4C 5x5 risk matrix
**Scope:** TASK-001 (Upgrade path documentation) + TASK-002 (Schema version checking)

```
DISCLAIMER: This guidance is AI-generated based on NASA Systems Engineering
standards. It is advisory only and does not constitute official NASA guidance.
```

---

## 1. Executive Summary

EN-006 introduces two changes to the ECW Status Line project: upgrade path documentation (TASK-001, docs-only) and schema version checking for config/state files (TASK-002, code change). While both tasks are individually low-risk, TASK-002 touches the config loading (`load_config`) and state management (`load_state`/`save_state`) hot paths -- the most critical code paths in the application. Incorrect implementation could break existing users' installations silently.

**Overall Risk Profile:**

| Category | High (Yellow+) | Medium | Low | Total |
|----------|----------------|--------|-----|-------|
| Technical Risks | 2 | 2 | 1 | 5 |
| Integration Risks | 1 | 2 | 0 | 3 |
| Documentation Risks | 0 | 2 | 1 | 3 |
| Regression Risks | 1 | 1 | 1 | 3 |
| **Total** | **4** | **7** | **3** | **14** |

**Key Finding:** The highest-risk area is backward compatibility for unversioned configs/state files. If the version checking code rejects or mishandles files that lack a `schema_version` field, every existing user's installation will break on upgrade. This is the single most important mitigation to get right.

---

## 2. Risk Identification

### 2.1 Technical Risks

#### RISK-EN006-001: Version Comparison Edge Cases

**Description:** Semantic version comparison is non-trivial. String comparison of version numbers produces incorrect results (e.g., `"2.10.0" < "2.9.0"` when compared lexicographically). Custom version parsing can fail on unexpected formats.

**Root Cause:** Python stdlib does not include a built-in semver comparator. The `packaging.version` module is a third-party dependency, and this project has a hard zero-dependency constraint (stdlib only).

**Likelihood:** M (Medium) -- Version comparison is a well-known problem with documented solutions, but the zero-dependency constraint limits options.

**Impact:** M -- Incorrect version comparison could cause false warnings (minor annoyance) or failure to warn on actual mismatches (silent data issues).

---

#### RISK-EN006-002: State File Schema Expansion Causes Corruption

**Description:** Adding a `schema_version` field to the state file (`ecw-statusline-state.json`) changes its structure. If the new version of the script writes a state file with `schema_version` and the user downgrades to an older version, the older script may fail to parse the state file or ignore the new field, leading to data loss or incorrect compaction detection.

**Root Cause:** The current `load_state()` function (lines 262-281) uses `json.load()` which returns whatever is in the file. It does not validate structure. The current `save_state()` function (lines 284-319) writes whatever dict is passed. An older version that encounters unexpected keys would silently pass them through, but if the schema changes in a more structural way, this could break.

**Likelihood:** L (Low) -- JSON's flexibility means extra keys are typically harmless in Python dicts. But if the schema version causes the code to take different code paths for reading/writing, downgrade becomes risky.

**Impact:** M -- State file corruption affects compaction detection only, which is a secondary feature. But it could trigger repeated false-positive compaction warnings.

---

#### RISK-EN006-003: Config File Schema Expansion Breaks deep_merge

**Description:** Adding `schema_version` as a top-level key in the config file could interact unexpectedly with the `deep_merge()` function (lines 211-219). If `schema_version` is a string in the default config but a user provides it as a dict (or vice versa), the merge behavior could produce unexpected results. More critically, if the version check happens *after* `deep_merge`, the user's config could override the expected schema version.

**Root Cause:** The `deep_merge()` function only recurses into dicts. For non-dict values, it uses simple replacement (`result[key] = value`). A `schema_version` string field would be safely overwritten. However, the *order of operations* matters: if version checking happens after config loading, the user could set `schema_version` to any value and bypass validation.

**Likelihood:** L (Low) -- The attack surface is limited since this is a local config file the user controls. But it creates a confusing user experience if version checking can be bypassed.

**Impact:** L -- Worst case is that version warnings are suppressed, which is low-severity since the feature is advisory.

---

#### RISK-EN006-004: Version Mismatch Warning Displayed on Every Invocation

**Description:** The status line script is invoked on every status update (potentially multiple times per second during active Claude Code sessions). If a version mismatch warning is emitted on every invocation, it will flood stderr or produce repeated visual noise in the status line output.

**Root Cause:** The script has no state persistence mechanism for "warning already shown." The state file tracks compaction data but not warning suppression. Adding suppression state increases state file complexity.

**Likelihood:** H (High) -- This is a near-certain consequence of naive implementation. The script is designed to be stateless between invocations (aside from compaction tracking), so any warning will repeat.

**Impact:** M -- Repeated warnings degrade user experience. If written to stdout, it corrupts the status line. If written to stderr, it may spam the terminal depending on how Claude Code handles stderr from status commands.

---

#### RISK-EN006-005: Performance Impact of Version Checking

**Description:** The status line script must complete in under ~100ms to avoid visible latency in the Claude Code UI. Adding version checking logic to both config loading and state loading adds I/O and parsing overhead.

**Root Cause:** The script currently loads config once per invocation and state once per invocation. Version checking adds comparison logic but no additional I/O. However, if the implementation adds file reads (e.g., reading a separate version file) or complex parsing, it could impact latency.

**Likelihood:** L (Low) -- Simple string comparison of a field already in the loaded JSON adds negligible overhead. Risk only materializes if implementation is over-engineered.

**Impact:** M -- Performance degradation in the status line is immediately noticeable to users as UI lag.

---

### 2.2 Integration Risks

#### RISK-EN006-006: Conflict with Existing Config Loading Path

**Description:** The `load_config()` function (lines 184-199) searches two paths (`CONFIG_PATHS`), loads the first found, and deep-merges with defaults. Adding schema version validation into this flow must not change the fallback behavior: if no config file exists, defaults must still work. If a config file exists but lacks `schema_version`, it must still be loaded (backward compatibility requirement).

**Root Cause:** The config loading path is a critical initialization sequence. Any change that adds a validation step must preserve the existing graceful-degradation contract.

**Likelihood:** M -- Moderate because the config loading code is straightforward, but insertion of validation logic between load and merge creates an opportunity for bugs in the conditional logic.

**Impact:** H -- If config loading fails, the entire script produces error output instead of a status line. Every user is affected.

---

#### RISK-EN006-007: State File Format Migration

**Description:** The current state file has three fields: `previous_context_tokens`, `last_compaction_from`, `last_compaction_to`. Adding `schema_version` is a format change. If the implementation also restructures the state (e.g., nesting existing fields under a `data` key), existing state files become incompatible.

**Root Cause:** No migration mechanism exists. The `load_state()` function returns a default dict if the file is missing or corrupt, but does not handle "valid JSON but wrong structure" scenarios.

**Likelihood:** L (Low) -- The acceptance criteria specify "backward compatibility for unversioned configs," implying additive-only changes. But implementation could drift from spec.

**Impact:** M -- Incompatible state file causes compaction detection to reset. Users lose compaction history but the script continues to function.

---

#### RISK-EN006-008: Interaction with `save_state()` Atomic Write Pattern

**Description:** The `save_state()` function (lines 284-319) uses an atomic write pattern (temp file + `os.replace`). Adding `schema_version` to the state dict is a simple addition that should not affect the write mechanism. However, if the implementation adds version-conditional write logic (e.g., "only write if version matches"), it could create a state where the file is never updated.

**Root Cause:** The atomic write pattern is robust but was designed for a specific state structure. Changes to the state dict content should be transparent to the write mechanism, but conditional logic around writes is risky.

**Likelihood:** L (Low) -- As long as `schema_version` is simply added to the dict before `json.dump()`, the atomic write works unchanged.

**Impact:** M -- If state writes are skipped due to version logic, compaction detection silently stops working.

---

### 2.3 Documentation Risks

#### RISK-EN006-009: Upgrade Documentation Becomes Stale

**Description:** TASK-001 adds upgrade instructions to `GETTING_STARTED.md`. If future versions change the config/state format again, the upgrade documentation will become stale and potentially misleading. The document is already 1,176 lines; adding more content increases maintenance burden.

**Root Cause:** Documentation is a snapshot of current state. Without a changelog or versioned docs, upgrade instructions for specific version pairs become technical debt.

**Likelihood:** M -- The project is actively evolving (v2.1.0 with multiple enablers in progress). Future format changes are probable.

**Impact:** M -- Stale upgrade docs cause user confusion but do not break functionality.

---

#### RISK-EN006-010: Incomplete Migration Paths

**Description:** The upgrade documentation may not cover all migration scenarios: fresh install, v2.0.0 to v2.1.0, config-file-only users, state-file-only users, users with custom configs that override default fields, users running in Docker containers where state files are ephemeral.

**Root Cause:** Migration paths are combinatorial. The number of user configurations grows exponentially with config options.

**Likelihood:** M -- Some edge cases will inevitably be missed in initial documentation.

**Impact:** L -- Missed migration paths affect a small subset of users. The script's graceful degradation (safe_get with defaults) limits actual breakage.

---

#### RISK-EN006-011: User Confusion About schema_version

**Description:** Adding a `schema_version` field to the config file creates a new concept that users must understand. Users may wonder: Should I set this? What value? What happens if I change it? Is it the same as the script version?

**Root Cause:** Schema versioning is an internal mechanism exposed to users through their config file. The boundary between "internal" and "user-facing" is blurred.

**Likelihood:** L -- Most users do not hand-edit config files; those who do are typically comfortable with versioned schemas.

**Impact:** L -- Confusion is self-resolving through documentation. No functional impact.

---

### 2.4 Regression Risks

#### RISK-EN006-012: Existing Test Suite Does Not Cover Version Checking

**Description:** The current test suite (`test_statusline.py`, 21 tests) tests the script via subprocess invocations with mock JSON payloads. None of the existing tests exercise config files with or without `schema_version`. New tests must be added, and existing tests must pass unchanged to confirm no regression.

**Root Cause:** The test suite is black-box (subprocess-based), which is good for regression detection but makes it difficult to unit-test internal functions like version comparison.

**Likelihood:** H (High) -- It is certain that the existing test suite does not cover the new feature. The risk is that implementation changes break existing tests without being caught during development.

**Impact:** M -- Test failures would be caught by CI, but if TASK-002 implementation changes default behavior (e.g., adds a warning message to stdout), it could cause false failures in existing tests that check output content.

---

#### RISK-EN006-013: Default Config Changes Affect All Users

**Description:** If `schema_version` is added to `DEFAULT_CONFIG` (lines 62-161), it changes the effective config for every user, including those without a config file. If any code path behaves differently based on the presence of `schema_version`, it changes behavior for all users.

**Root Cause:** The `DEFAULT_CONFIG` dict is the baseline for all script behavior. Any change to it has global effect.

**Likelihood:** M -- The field addition itself is safe (Python dicts accept new keys). The risk is in code that branches on the field's presence.

**Impact:** M -- Behavioral change for all users is significant, but if limited to adding an informational warning, the impact is moderate.

---

#### RISK-EN006-014: Config File Round-Trip Fidelity

**Description:** Users who have existing `ecw-statusline-config.json` files will not have `schema_version` in them. When the script loads their config and deep-merges with defaults, the default `schema_version` will be present in the merged result. This is correct behavior. However, if any tooling or future feature writes the merged config back to disk, it would add `schema_version` to the user's file, potentially surprising them.

**Root Cause:** The script currently never writes config files (only state files). But if this invariant changes in the future, config round-tripping becomes a concern.

**Likelihood:** L (Low) -- The script does not write config files, and TASK-002 does not add this capability.

**Impact:** L -- Hypothetical future risk only.

---

## 3. Risk Register

| ID | Risk | Likelihood | Impact | Score | Mitigation | Residual |
|---|---|---|---|---|---|---|
| RISK-EN006-001 | Version comparison edge cases (lexicographic vs semantic) | M | M | 6 (YELLOW) | Use tuple comparison `(major, minor, patch)` parsed from version string; validate format with regex | L-L = 2 (GREEN) |
| RISK-EN006-002 | State file schema expansion causes corruption on downgrade | L | M | 4 (GREEN) | Additive-only changes; old scripts ignore unknown keys; document downgrade behavior | L-L = 2 (GREEN) |
| RISK-EN006-003 | Config schema_version interacts with deep_merge unexpectedly | L | L | 2 (GREEN) | Place schema_version at top level as string; test merge with/without user override | L-L = 1 (GREEN) |
| RISK-EN006-004 | Version mismatch warning repeats on every invocation | H | M | 9 (YELLOW) | Use state file to track "warning shown" flag; or emit warning via debug_log only (stderr, debug mode) | L-L = 2 (GREEN) |
| RISK-EN006-005 | Performance impact of version checking | L | M | 4 (GREEN) | Keep version check as simple string comparison on already-loaded JSON; no additional I/O | L-L = 1 (GREEN) |
| RISK-EN006-006 | Conflict with config loading path breaks all users | M | H | 9 (YELLOW) | Version check must be advisory-only; never reject a config file; always fall through to defaults | L-L = 2 (GREEN) |
| RISK-EN006-007 | State file format migration incompatibility | L | M | 4 (GREEN) | Additive-only: add `schema_version` key but do not restructure existing fields | L-L = 1 (GREEN) |
| RISK-EN006-008 | Version logic interferes with atomic write pattern | L | M | 4 (GREEN) | Do not add conditional write logic; always write state including version field | L-L = 1 (GREEN) |
| RISK-EN006-009 | Upgrade documentation becomes stale over time | M | M | 6 (YELLOW) | Keep upgrade docs version-specific; consider separate CHANGELOG.md in future | M-L = 3 (GREEN) |
| RISK-EN006-010 | Incomplete migration path coverage | M | L | 4 (GREEN) | Cover top 3 scenarios: fresh install, upgrade with config, upgrade without config | L-L = 2 (GREEN) |
| RISK-EN006-011 | User confusion about schema_version field purpose | L | L | 2 (GREEN) | Document that schema_version is auto-managed; users should not set it manually | L-L = 1 (GREEN) |
| RISK-EN006-012 | Existing tests do not cover version checking; new code could break them | H | M | 9 (YELLOW) | Run full test suite before and after changes; add new tests for version checking; ensure no stdout changes | M-L = 3 (GREEN) |
| RISK-EN006-013 | DEFAULT_CONFIG changes affect all users globally | M | M | 6 (YELLOW) | schema_version in DEFAULT_CONFIG should be informational only; no behavioral branching on its absence | L-L = 2 (GREEN) |
| RISK-EN006-014 | Config file round-trip fidelity (hypothetical) | L | L | 2 (GREEN) | Do not write config files; document this invariant | L-L = 1 (GREEN) |

---

## 4. Risk-Based Implementation Order

Based on the risk analysis, the recommended implementation order minimizes exposure to the highest-scoring risks:

### Phase 1: TASK-001 -- Upgrade Path Documentation (Zero-risk foundation)
**Rationale:** Documentation changes carry no regression risk. Completing TASK-001 first provides the user-facing context for TASK-002 changes.

1. Add "Upgrading" section to `GETTING_STARTED.md`
2. Cover three migration scenarios:
   - Fresh install (no changes needed)
   - Upgrade with existing config file (no changes needed; new fields auto-populated from defaults)
   - Upgrade with existing state file (auto-migrated; old format still accepted)
3. Document the new `schema_version` concept (what it is, why it exists, user should not edit it)

### Phase 2: TASK-002 -- Schema Version Checking (Risk-mitigated implementation)
**Rationale:** Address RISK-EN006-006 (config loading) first, then RISK-EN006-004 (warning frequency), then RISK-EN006-012 (test coverage).

1. **Add `schema_version` to DEFAULT_CONFIG** (top-level string field, e.g., `"1.0"`)
   - Mitigates: RISK-EN006-003, RISK-EN006-013
   - The field is purely informational until step 3

2. **Add `schema_version` to state file** (additive field in `save_state`)
   - Mitigates: RISK-EN006-002, RISK-EN006-007, RISK-EN006-008
   - `load_state()` reads it if present, ignores if absent

3. **Add version comparison utility** (pure function, no I/O)
   - Mitigates: RISK-EN006-001
   - Parse "major.minor" into tuple; compare tuples
   - Validate format with regex; return `None` on invalid format

4. **Add advisory version check in `load_config()`** (after merge, before return)
   - Mitigates: RISK-EN006-006
   - Compare user config's `schema_version` (if present) with DEFAULT_CONFIG's `schema_version`
   - If mismatch: `debug_log()` warning only (RISK-EN006-004 mitigation)
   - Never reject config; never modify config; never alter return value

5. **Add advisory version check in `load_state()`** (after load, before return)
   - Same pattern: debug_log warning on mismatch, never reject

6. **Add tests for version checking** (new test functions)
   - Mitigates: RISK-EN006-012
   - Test: config without schema_version loads successfully
   - Test: config with matching schema_version loads successfully
   - Test: config with mismatched schema_version loads successfully (with debug warning)
   - Test: state file without schema_version loads successfully
   - Run full existing test suite to confirm no regressions

---

## 5. Top 3 Mitigations (with Code-Level Guidance)

### Mitigation 1: Advisory-Only Version Checking (RISK-EN006-004, RISK-EN006-006)

**Problem:** Version mismatch detection must not break existing users or produce noisy output.

**Code-level guidance:**

```python
# Add to DEFAULT_CONFIG (top-level, alongside "display", "segments", etc.):
DEFAULT_CONFIG: Dict[str, Any] = {
    "schema_version": "1.0",   # Config schema version
    # ... existing sections ...
}

# Add version check function (place near load_config):
def _check_schema_version(loaded: Dict, expected: str, source: str) -> None:
    """Advisory check: warn if schema version mismatches. Never rejects data."""
    loaded_version = loaded.get("schema_version")
    if loaded_version is None:
        # Unversioned file (pre-EN006). This is normal for upgrades.
        debug_log(f"{source}: no schema_version found (pre-EN006 format, OK)")
        return
    if loaded_version != expected:
        debug_log(
            f"{source}: schema_version mismatch: "
            f"found '{loaded_version}', expected '{expected}'. "
            f"Config will still be loaded. Consider upgrading."
        )

# Insert into load_config() AFTER deep_merge, BEFORE return:
def load_config() -> Dict[str, Any]:
    config = deep_copy(DEFAULT_CONFIG)
    for config_path in CONFIG_PATHS:
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                # >>> NEW: Advisory version check on raw user config <<<
                _check_schema_version(
                    user_config,
                    DEFAULT_CONFIG["schema_version"],
                    f"config:{config_path}"
                )
                config = deep_merge(config, user_config)
                debug_log(f"Loaded config from {config_path}")
                break
            except (json.JSONDecodeError, IOError) as e:
                debug_log(f"Config load error from {config_path}: {e}")
    return config
```

**Key design decisions:**
- Warning goes to `debug_log()` (stderr, debug mode only) -- not stdout, not the status line
- `_check_schema_version` takes the raw user config (before merge) to detect the actual file content
- The function never raises, never returns an error, never modifies the config
- Missing `schema_version` is explicitly logged as "OK" (backward compatibility)

---

### Mitigation 2: Additive-Only State File Changes (RISK-EN006-002, RISK-EN006-007)

**Problem:** The state file format must be extended without breaking older script versions or losing existing compaction data.

**Code-level guidance:**

```python
# In load_state(), add schema_version to the default dict:
def load_state(config: Dict) -> Dict[str, Any]:
    default = {
        "schema_version": "1.0",          # NEW
        "previous_context_tokens": 0,
        "last_compaction_from": 0,
        "last_compaction_to": 0,
    }
    state_file = _resolve_state_path(config)
    if state_file is None:
        return default
    try:
        if state_file.exists():
            with open(state_file, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            # >>> NEW: Advisory version check <<<
            _check_schema_version(
                loaded,
                default["schema_version"],
                f"state:{state_file}"
            )
            # Merge loaded over defaults to preserve new default fields
            # while keeping any existing values from the file
            merged = {**default, **loaded}
            return merged
    except (json.JSONDecodeError, OSError) as e:
        debug_log(f"State load error: {e}")
    return default

# In save_state(), ensure schema_version is always written:
def save_state(config: Dict, state: Dict[str, Any]) -> None:
    state_file = _resolve_state_path(config)
    if state_file is None:
        return
    # Ensure schema_version is present in saved state
    state.setdefault("schema_version", "1.0")
    # ... rest of atomic write logic unchanged ...
```

**Key design decisions:**
- `load_state()` uses `{**default, **loaded}` to merge: new default fields are populated for old state files, existing fields are preserved
- `schema_version` is added to the default dict, so old state files without it get the default automatically
- `save_state()` uses `setdefault` to add version without overwriting if already present
- An older script version that reads a state file with `schema_version` will simply ignore the extra key (Python dict behavior)

---

### Mitigation 3: Version Comparison Without External Dependencies (RISK-EN006-001)

**Problem:** Version string comparison must be correct and stdlib-only.

**Code-level guidance:**

```python
def _parse_schema_version(version_str: str) -> Optional[Tuple[int, ...]]:
    """Parse a schema version string into a comparable tuple.

    Accepts formats like "1.0", "1.0.0", "2.1".
    Returns None for invalid formats (never raises).
    """
    if not isinstance(version_str, str):
        return None
    # Match 1-3 numeric segments separated by dots
    match = re.match(r'^(\d+)(?:\.(\d+))?(?:\.(\d+))?$', version_str)
    if not match:
        return None
    parts = [int(g) for g in match.groups() if g is not None]
    return tuple(parts)


def _is_version_compatible(loaded: str, expected: str) -> bool:
    """Check if loaded schema version is compatible with expected.

    Compatibility rule: major version must match.
    Minor version of loaded may be <= expected (older config is fine).
    Returns True if compatible or if either version cannot be parsed.
    """
    loaded_t = _parse_schema_version(loaded)
    expected_t = _parse_schema_version(expected)
    if loaded_t is None or expected_t is None:
        return True  # Cannot determine; assume compatible
    # Major version must match
    if loaded_t[0] != expected_t[0]:
        return False
    return True
```

**Key design decisions:**
- Uses `re.match` (already imported in statusline.py, line 41) -- no new imports
- Returns `None` on parse failure rather than raising -- consistent with project's error-handling philosophy
- Compatibility is defined at major version level only -- minor version differences are informational
- `_is_version_compatible` returns `True` on parse failure -- fail-open, never reject
- Tuple comparison avoids lexicographic string comparison bugs
- The regex pattern is anchored (`^...$`) to prevent partial matches

---

## 6. Relationship to Existing Risk Register

Several risks identified in this assessment relate to entries in the existing XPLAT risk register (`docs/risks/XPLAT-001-e-008-risk-register.md`):

| EN-006 Risk | Related XPLAT Risk | Relationship |
|---|---|---|
| RISK-EN006-001 (Version comparison) | RSK-XPLAT-016 (Claude Code JSON Schema Changes) | EN-006 partially mitigates XPLAT-016 by adding schema version awareness |
| RISK-EN006-002 (State file expansion) | RSK-XPLAT-022 (State File Corruption) | EN-006 must not reintroduce corruption risk that EN-005 mitigated via atomic writes |
| RISK-EN006-006 (Config loading conflict) | RSK-XPLAT-023 (Config File Permission Issues) | EN-006 version checking must preserve the existing graceful-degradation contract |
| RISK-EN006-009 (Stale upgrade docs) | RSK-XPLAT-020 (No Upgrade Path Documentation) | EN-006 TASK-001 directly addresses XPLAT-020 |
| RISK-EN006-012 (Test coverage gap) | RSK-XPLAT-007 (CI/CD Pipeline) | New tests must run in the existing CI pipeline |

---

## 7. Residual Risk Summary

After implementation of all recommended mitigations:

| Score Range | Count | Risks |
|---|---|---|
| GREEN (1-3) | 12 | RISK-EN006-002, 003, 005, 007, 008, 010, 011, 014, and mitigated 001, 004, 006, 012 |
| YELLOW (4-6) | 2 | RISK-EN006-009 (stale docs, inherent), RISK-EN006-013 (global config change, inherent) |
| RED (>6) | 0 | None |

**Conclusion:** EN-006 is safe to implement with the recommended mitigations. The highest pre-mitigation risks (RISK-EN006-004, RISK-EN006-006, RISK-EN006-012, all score 9) are fully addressable through the advisory-only design pattern and comprehensive test coverage. No blocking risks remain after mitigation.

---

*Risk assessment generated by nse-risk agent for EN-006 orchestration (en006-20260212-001)*
*Methodology: NASA NPR 7123.1D Systems Engineering / NPR 8000.4C Risk Management*
