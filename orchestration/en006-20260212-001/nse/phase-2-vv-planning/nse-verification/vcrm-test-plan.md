# EN-006 Verification Cross-Reference Matrix (VCRM)

> **Document ID:** NSE-VCRM-EN006-001
> **Version:** 1.0
> **Date:** 2026-02-12
> **Author:** nse-verification agent
> **Status:** DRAFT
> **Orchestration:** en006-20260212-001
> **Method:** NASA NPR 7123.1D Process 7 (Technical Verification)

```
DISCLAIMER: This guidance is AI-generated based on NASA Systems Engineering
standards. It is advisory only and does not constitute official NASA guidance.
```

---

## 1. Verification Summary

### 1.1 Scope

This VCRM maps all 24 requirements from NSE-REQ-EN006-001 and all 14 risks from the EN-006 Risk Assessment to specific verification methods, test procedures, and acceptance thresholds. It covers both TASK-001 (Upgrade Path Documentation) and TASK-002 (Schema Version Checking).

### 1.2 Verification Method Key

| Code | Method | Description | Applicable To |
|------|--------|-------------|---------------|
| **T** | Test | Automated test in `test_statusline.py` via subprocess invocation | Code behavior |
| **I** | Inspection | Manual or scripted review of file contents, structure, or style | Documentation, code structure |
| **A** | Analysis | Static analysis or logical reasoning about code properties | Performance, compatibility |
| **D** | Demonstration | Running the script and observing behavior in a representative scenario | Integration, end-to-end |

### 1.3 Test Inventory Summary

| Source | Count | Status |
|--------|-------|--------|
| Existing tests (pre-EN-006) | 22 | PASS (regression baseline) |
| New RED-phase tests (impl pipeline) | 6 | 1 PASS, 5 FAIL (expected) |
| Additional V&V procedures (this document) | 12 | NOT YET IMPLEMENTED |
| **Total verification procedures** | **40** | -- |

### 1.4 Coverage Gap Summary (from Barrier-1 Handoff)

The RED phase test inventory identified 4 coverage gaps:
1. No test for version comparison logic (tuple comparison)
2. No test for state file version mismatch (only config mismatch tested)
3. No test for downgrade scenario (newer state file read by older script)
4. Backward-compat test validates existing behavior but does not test transition path

This VCRM addresses all 4 gaps via recommended additional verification procedures.

---

## 2. Requirements Traceability Matrix

### 2.1 TASK-001: Upgrade Path Documentation (REQ-EN006-001 through REQ-EN006-006, REQ-EN006-024)

| Req ID | Requirement Summary | Method | Test/Procedure ID | Expected Result | Priority | Risk Link |
|--------|---------------------|--------|-------------------|-----------------|----------|-----------|
| REQ-EN006-001 | Upgrading section exists in GETTING_STARTED.md, linked from TOC | T + I | `run_upgrade_docs_exist_test` + INSP-001 | Test: regex matches heading containing "Upgrade" or "Migration". Inspection: TOC link resolves to section. | P1 | RISK-009 |
| REQ-EN006-002 | Step-by-step version migration instructions (macOS, Windows, Linux) | I | INSP-002 | Inspection confirms: (a) platform-specific command blocks exist, (b) download/copy step present, (c) verification step present, (d) config preservation noted. | P2 | RISK-010 |
| REQ-EN006-003 | Config file migration guidance (deep_merge behavior) | I | INSP-003 | Inspection confirms: (a) config preservation statement present, (b) new key defaults explanation, (c) removed key behavior explanation. All statements match actual `load_config()` + `deep_merge()` behavior. | P2 | RISK-009, RISK-010 |
| REQ-EN006-004 | State file compatibility guidance | I | INSP-004 | Inspection confirms: (a) auto-managed statement, (b) fallback-to-defaults statement, (c) safe-to-delete guidance. All match `load_state()` behavior. | P2 | RISK-007, RISK-009 |
| REQ-EN006-005 | Breaking changes subsection with conventions | I | INSP-005 | Inspection confirms: (a) "Breaking Changes" subsection exists, (b) current breaking changes documented (if any), (c) categories of breaking changes listed, (d) future convention established. | P3 | RISK-009 |
| REQ-EN006-006 | Version identification command | I + D | INSP-006 + DEMO-001 | Inspection: command documented. Demonstration: command produces correct version string when run against current `statusline.py`. | P3 | -- |
| REQ-EN006-024 | Documentation follows GETTING_STARTED.md style | I | INSP-007 | Inspection confirms: (a) platform-specific code blocks used, (b) expected output examples where applicable, (c) consistent markdown formatting, (d) consistent heading hierarchy. | P2 | RISK-009 |

### 2.2 TASK-002: Schema Version Checking (REQ-EN006-010 through REQ-EN006-018)

| Req ID | Requirement Summary | Method | Test/Procedure ID | Expected Result | Priority | Risk Link |
|--------|---------------------|--------|-------------------|-----------------|----------|-----------|
| REQ-EN006-010 | `SCHEMA_VERSION` constant defined in statusline.py | T + I | `run_schema_version_in_config_test` + INSP-008 | Test: imports DEFAULT_CONFIG successfully, `schema_version` key exists and has non-empty string value. Inspection: constant exists at module level. | P1 | RISK-001, RISK-013 |
| REQ-EN006-011 | `save_state()` includes `schema_version` in output JSON | T | `run_schema_version_in_state_test` | After script execution with a writable state path, the JSON file contains `"schema_version"` key with the correct value. | P1 | RISK-002, RISK-008 |
| REQ-EN006-012 | `DEFAULT_CONFIG` includes top-level `schema_version` | T | `run_schema_version_in_config_test` | `DEFAULT_CONFIG["schema_version"]` exists and equals `SCHEMA_VERSION`. | P1 | RISK-003, RISK-013 |
| REQ-EN006-013 | Unversioned config files load without warning or error | T | `run_unversioned_config_backward_compat_test` | Config file without `schema_version` loads; script produces output; no "mismatch" or "outdated" text in stdout/stderr. | P1 (critical) | RISK-006 |
| REQ-EN006-014 | Unversioned state files load without warning or error | T | ADDL-TEST-001 (recommended) | State file without `schema_version` loads; script produces normal output; no crash; no stderr warning. | P1 (critical) | RISK-007 |
| REQ-EN006-015 | Config version mismatch emits debug_log warning | T | `run_schema_version_mismatch_warning_test` | Config with mismatched `schema_version` triggers combined output containing "version" AND ("mismatch" OR "outdated" OR "upgrade" OR "warning") or a warning icon. Script exits 0. | P1 | RISK-004, RISK-006 |
| REQ-EN006-016 | State version mismatch emits debug_log warning and resets state | T | ADDL-TEST-002 (recommended) | State file with mismatched `schema_version` causes debug warning and state values reset to defaults (compaction counters at 0). | P1 | RISK-002, RISK-007 |
| REQ-EN006-017 | Schema checking does not alter stdout output | T + A | `run_schema_version_match_no_warning_test` + `run_unversioned_config_backward_compat_test` + ADDL-TEST-003 (recommended) | Stdout output is identical with and without `schema_version` in config/state when `ECW_DEBUG` is not set. All version messages go to stderr only. | P1 (critical) | RISK-004 |
| REQ-EN006-018 | `schema_version` in DEFAULT_CONFIG not overridable by user config | T | ADDL-TEST-004 (recommended) | After loading a config with `schema_version: "999"`, the effective config's `schema_version` equals `SCHEMA_VERSION`, not `"999"`. | P2 | RISK-003 |

### 2.3 Non-Functional Requirements (REQ-EN006-020 through REQ-EN006-023)

| Req ID | Requirement Summary | Method | Test/Procedure ID | Expected Result | Priority | Risk Link |
|--------|---------------------|--------|-------------------|-----------------|----------|-----------|
| REQ-EN006-020 | Zero external dependencies preserved | I + A | INSP-009 | Inspection: `statusline.py` import section contains only stdlib modules (`json`, `sys`, `os`, `re`, `pathlib`, `copy`, `tempfile`, etc.). No `pip install` or `requirements.txt` changes. | P1 | -- |
| REQ-EN006-021 | Single-file deployment preserved | I + T | INSP-010 + regression suite | Inspection: no new `.py` files added as runtime dependencies. Test: all 22 existing tests pass (proves script works standalone). | P1 | -- |
| REQ-EN006-022 | Python 3.9 compatibility | T + A | CI pipeline (Python 3.9 matrix) + INSP-011 | CI passes on Python 3.9. Inspection: no `match` statements, no `X \| Y` union syntax, no walrus operator in unsupported contexts. | P1 | -- |
| REQ-EN006-023 | Negligible performance impact | A | ANALYSIS-001 | Analysis: no additional file I/O beyond existing `load_config()` and `load_state()` reads. Version check is a string comparison on already-loaded data. | P3 | RISK-005 |

### 2.4 Interface Requirements (REQ-EN006-030 through REQ-EN006-033)

| Req ID | Requirement Summary | Method | Test/Procedure ID | Expected Result | Priority | Risk Link |
|--------|---------------------|--------|-------------------|-----------------|----------|-----------|
| REQ-EN006-030 | Config file JSON schema extended with optional `schema_version` | T + I | `run_schema_version_in_config_test` + `run_unversioned_config_backward_compat_test` | Config files with and without `schema_version` both load successfully. | P1 | RISK-003, RISK-006 |
| REQ-EN006-031 | State file JSON schema extended with `schema_version` | T | `run_schema_version_in_state_test` | Saved state file contains `schema_version` field. | P1 | RISK-002, RISK-008 |
| REQ-EN006-032 | Function signatures unchanged | I | INSP-012 | Inspection confirms signatures remain: `load_config() -> Dict[str, Any]`, `load_state(config: Dict) -> Dict[str, Any]`, `save_state(config: Dict, state: Dict[str, Any]) -> None`, `deep_merge(base: Dict, override: Dict) -> Dict`. | P1 | RISK-006 |
| REQ-EN006-033 | Stdin/stdout interface unchanged | T | Full regression suite (22 existing tests) | All 22 pre-EN-006 tests pass without modification. Stdout output format unchanged. | P1 | RISK-012 |

---

## 3. Risk-Based Verification

### 3.1 Risk-to-Verification Mapping

| Risk ID | Risk Description | Pre-Mitigation Score | Verification Method | Test/Procedure | Acceptance Threshold | Residual Score |
|---------|------------------|---------------------|---------------------|----------------|---------------------|----------------|
| RISK-EN006-001 | Version comparison edge cases (lexicographic vs semantic) | 6 (YELLOW) | T + A | ADDL-TEST-005 (recommended) + ANALYSIS-002 | Version comparison uses tuple-based parsing, not string comparison. Regex validates format. Returns compatible on parse failure. | 2 (GREEN) |
| RISK-EN006-002 | State file schema expansion causes corruption on downgrade | 4 (GREEN) | T + I | `run_schema_version_in_state_test` + INSP-013 | State file change is additive-only (new key, no restructuring). Old scripts ignore unknown keys. | 2 (GREEN) |
| RISK-EN006-003 | Config `schema_version` interacts with `deep_merge` unexpectedly | 2 (GREEN) | T | ADDL-TEST-004 + `run_unversioned_config_backward_compat_test` | User-supplied `schema_version` does not override internal version. deep_merge handles string field correctly. | 1 (GREEN) |
| RISK-EN006-004 | Version mismatch warning repeats on every invocation | 9 (YELLOW) | T + I | `run_schema_version_mismatch_warning_test` + INSP-014 | Warnings emitted via `debug_log()` only (stderr, `ECW_DEBUG=1`). No stdout pollution. Acceptable to repeat since debug mode is opt-in. | 2 (GREEN) |
| RISK-EN006-005 | Performance impact of version checking | 4 (GREEN) | A | ANALYSIS-001 | No additional file I/O. Version check is O(1) string comparison on already-loaded dict. | 1 (GREEN) |
| RISK-EN006-006 | Conflict with config loading path breaks all users | 9 (YELLOW) | T | `run_unversioned_config_backward_compat_test` + full regression suite (22 tests) | Config loading never rejects a file. Version check is advisory-only. All existing tests pass. | 2 (GREEN) |
| RISK-EN006-007 | State file format migration incompatibility | 4 (GREEN) | T + I | ADDL-TEST-001 + INSP-013 | State file change is additive. `load_state()` returns defaults on any error. Missing `schema_version` treated as current. | 1 (GREEN) |
| RISK-EN006-008 | Version logic interferes with atomic write pattern | 4 (GREEN) | T | `run_schema_version_in_state_test` + `run_atomic_write_test` (existing) | State file written successfully with `schema_version`. Atomic write pattern (temp + rename) unchanged. No orphan .tmp files. | 1 (GREEN) |
| RISK-EN006-009 | Upgrade documentation becomes stale | 6 (YELLOW) | I | INSP-005 + INSP-007 | Breaking changes convention established. Version-specific instructions present. Style consistent. | 3 (GREEN) |
| RISK-EN006-010 | Incomplete migration path coverage | 4 (GREEN) | I | INSP-002 + INSP-003 + INSP-004 | Top 3 scenarios covered: fresh install, upgrade with config, upgrade with state. Platform-specific commands for macOS/Windows/Linux. | 2 (GREEN) |
| RISK-EN006-011 | User confusion about `schema_version` field | 2 (GREEN) | I | INSP-015 | Documentation states that `schema_version` is auto-managed. Users advised not to set it manually. | 1 (GREEN) |
| RISK-EN006-012 | Existing tests do not cover version checking | 9 (YELLOW) | T | Full regression suite + 6 new EN-006 tests + recommended ADDL tests | All 22 existing tests pass (no regression). All 6 new tests pass (feature verified). Additional tests cover identified gaps. | 3 (GREEN) |
| RISK-EN006-013 | DEFAULT_CONFIG changes affect all users | 6 (YELLOW) | T + A | Full regression suite + ANALYSIS-003 | Adding `schema_version` to DEFAULT_CONFIG does not change any code path behavior. Existing tests pass unchanged. No behavioral branching on field absence. | 2 (GREEN) |
| RISK-EN006-014 | Config file round-trip fidelity | 2 (GREEN) | I | INSP-016 | Inspection confirms: script does not write config files. No new config-writing code added. | 1 (GREEN) |

---

## 4. Test Procedures

### 4.1 Automated Tests (from test_statusline.py)

These are the 6 tests written by the ps-tdd-red agent in the RED phase. All are subprocess-based black-box tests.

#### T-001: `run_schema_version_in_config_test`
- **Req coverage:** REQ-EN006-010, REQ-EN006-012
- **Risk coverage:** RISK-EN006-001, RISK-EN006-013
- **Mechanism:** Imports `DEFAULT_CONFIG` from `statusline.py` via Python subprocess and checks for `schema_version` key presence and non-empty value.
- **Pass criteria:** Exit code 0. JSON output `{"has_schema_version": true, "value": "<non-empty>"}`.
- **Current status:** FAIL (schema_version key does not exist yet)

#### T-002: `run_schema_version_in_state_test`
- **Req coverage:** REQ-EN006-011, REQ-EN006-031
- **Risk coverage:** RISK-EN006-002, RISK-EN006-008
- **Mechanism:** Runs script with a writable temp state file path. After execution, reads the state JSON and checks for `schema_version` key.
- **Pass criteria:** State file exists, is valid JSON, and contains `"schema_version"` key.
- **Current status:** FAIL (save_state does not write schema_version)

#### T-003: `run_schema_version_mismatch_warning_test`
- **Req coverage:** REQ-EN006-015
- **Risk coverage:** RISK-EN006-004, RISK-EN006-006
- **Mechanism:** Creates config with `{"schema_version": "0.0.1"}` (deliberate mismatch). Runs script and checks combined stdout+stderr for version-related warning text.
- **Pass criteria:** Exit code 0. Combined output contains "version" AND at least one of ("mismatch", "outdated", "upgrade", "warning") or a warning icon.
- **Current status:** FAIL (no version checking logic implemented)

#### T-004: `run_unversioned_config_backward_compat_test`
- **Req coverage:** REQ-EN006-013, REQ-EN006-030
- **Risk coverage:** RISK-EN006-006
- **Mechanism:** Creates config `{"cost": {"currency_symbol": "$"}}` without `schema_version`. Runs script and verifies it produces output without crash or mismatch warning.
- **Pass criteria:** Exit code 0. Non-empty stdout. No "mismatch" or "outdated" text in combined output.
- **Current status:** PASS (existing behavior already correct)

#### T-005: `run_schema_version_match_no_warning_test`
- **Req coverage:** REQ-EN006-017
- **Risk coverage:** RISK-EN006-004
- **Mechanism:** Reads expected version from `DEFAULT_CONFIG`. Creates config with matching `schema_version`. Verifies no warning in output.
- **Pass criteria:** Exit code 0. Non-empty stdout. No "mismatch", "outdated", or warning icon in combined output.
- **Current status:** FAIL (DEFAULT_CONFIG has no schema_version, so expected version is empty string)

#### T-006: `run_upgrade_docs_exist_test`
- **Req coverage:** REQ-EN006-001
- **Risk coverage:** RISK-EN006-009
- **Mechanism:** Reads `GETTING_STARTED.md` and searches for markdown heading matching regex `^#{1,3}\s+.*(?:Upgrade|Migration|Upgrading|Migrating).*$`.
- **Pass criteria:** At least one heading match found.
- **Current status:** FAIL (no upgrade section in GETTING_STARTED.md)

### 4.2 Recommended Additional Automated Tests

These tests address coverage gaps identified in the Barrier-1 handoff and risk assessment.

#### ADDL-TEST-001: Unversioned State File Backward Compatibility
- **Req coverage:** REQ-EN006-014
- **Risk coverage:** RISK-EN006-007
- **Rationale:** Gap #2 from handoff -- no test for state file without `schema_version`.
- **Mechanism:** Create a state file with only the 3 original fields (`previous_context_tokens`, `last_compaction_from`, `last_compaction_to`) and no `schema_version`. Run the script with this state file. Verify:
  1. Script exits 0 with non-empty stdout
  2. No "mismatch" or error text in stderr
  3. Compaction detection still works (state is loaded correctly)
- **Priority:** P1 -- directly addresses the highest-risk area (backward compatibility)

#### ADDL-TEST-002: State File Version Mismatch Warning and Reset
- **Req coverage:** REQ-EN006-016
- **Risk coverage:** RISK-EN006-002, RISK-EN006-007
- **Rationale:** Gap #2 from handoff -- only config mismatch is tested, not state mismatch.
- **Mechanism:** Create a state file with `{"schema_version": "0.0.1", "previous_context_tokens": 180000, "last_compaction_from": 100000, "last_compaction_to": 50000}`. Run the script with `ECW_DEBUG=1`. Verify:
  1. Script exits 0 with non-empty stdout
  2. Stderr contains version-related warning text
  3. State is reset to defaults (no compaction icon in output despite high `previous_context_tokens` in file)
- **Priority:** P1 -- covers REQ-EN006-016 which has no existing test

#### ADDL-TEST-003: Schema Version Checking Does Not Pollute Stdout
- **Req coverage:** REQ-EN006-017
- **Risk coverage:** RISK-EN006-004
- **Rationale:** Explicit verification that version warnings go to stderr only.
- **Mechanism:** Run script twice with same payload:
  1. With config `{"schema_version": "0.0.1"}` (mismatch) and `ECW_DEBUG` NOT set
  2. With no config file (default behavior)
  Compare stdout from both runs. They must be identical (same bytes).
- **Priority:** P1 -- protects the display-critical output path

#### ADDL-TEST-004: Schema Version Not Overridable by User Config
- **Req coverage:** REQ-EN006-018
- **Risk coverage:** RISK-EN006-003
- **Rationale:** Ensures internal version cannot be spoofed via user config.
- **Mechanism:** Create config with `{"schema_version": "999.0"}`. Import `DEFAULT_CONFIG` and the effective config after merge. Verify that the effective `schema_version` equals `SCHEMA_VERSION`, not `"999.0"`.
- **Priority:** P2 -- important for integrity but low exploitation risk

#### ADDL-TEST-005: Version Comparison Logic (Tuple-Based)
- **Req coverage:** REQ-EN006-010 (implicitly)
- **Risk coverage:** RISK-EN006-001
- **Rationale:** Gap #1 from handoff -- no test for version comparison logic.
- **Mechanism:** If a `_parse_schema_version()` or `_is_version_compatible()` function is implemented, test via import:
  1. `"1"` vs `"1"` -> compatible
  2. `"1"` vs `"2"` -> incompatible (major mismatch)
  3. `"1.0"` vs `"1.1"` -> compatible (minor difference, same major)
  4. `"abc"` vs `"1"` -> compatible (fail-open on parse error)
  5. `""` vs `"1"` -> compatible (fail-open)
  If version comparison is a simple string equality (as per requirements recommending integer strings), test:
  1. `"1"` == `"1"` -> match
  2. `"1"` != `"2"` -> mismatch
- **Priority:** P2 -- defensive test; current design uses simple string comparison

### 4.3 Inspection Procedures (Manual/Visual)

#### INSP-001: Upgrade Section TOC Integration
- **Req:** REQ-EN006-001
- **Procedure:** Open `GETTING_STARTED.md`. Verify the Table of Contents contains a link to the Upgrading section. Click the link (or search for anchor) to confirm it resolves correctly.
- **Pass:** TOC entry exists and links to correct section.

#### INSP-002: Platform-Specific Migration Commands
- **Req:** REQ-EN006-002
- **Procedure:** Review the Upgrading section in `GETTING_STARTED.md`. Confirm:
  1. macOS command block exists with valid shell syntax
  2. Windows command block exists (PowerShell or cmd)
  3. Linux command block exists with valid shell syntax
  4. Each block includes download/copy, verification, and config preservation steps
- **Pass:** All 3 platforms covered with syntactically correct commands.

#### INSP-003: Config File Migration Accuracy
- **Req:** REQ-EN006-003
- **Procedure:** Review documented config migration behavior. Cross-reference with `load_config()` (lines ~184-199) and `deep_merge()` (lines ~211-219) in `statusline.py`. Verify:
  1. "Config files are preserved" matches reality (separate file from script)
  2. "New keys use defaults" matches `deep_merge` behavior (base provides defaults)
  3. "Old keys silently ignored" matches `deep_merge` behavior (override adds unknown keys to result, but they are unused)
- **Pass:** All documented behaviors match code behavior.

#### INSP-004: State File Documentation Accuracy
- **Req:** REQ-EN006-004
- **Procedure:** Review documented state file behavior. Cross-reference with `load_state()` (lines ~262-281). Verify:
  1. "Auto-managed" claim is accurate
  2. "Falls back to defaults on error" matches the try/except in `load_state()`
  3. "Safe to delete" is accurate (script creates defaults if file missing)
- **Pass:** All documented behaviors match code behavior.

#### INSP-005: Breaking Changes Convention
- **Req:** REQ-EN006-005
- **Procedure:** Review the Breaking Changes subsection. Verify:
  1. Subsection heading exists (e.g., `### Breaking Changes` or similar)
  2. Current version's breaking changes documented (may be "None for v2.1.0")
  3. Categories listed: removed config keys, changed default behavior, changed output format
  4. Convention for future documentation established (e.g., "each version lists its breaking changes here")
- **Pass:** All 4 elements present.

#### INSP-006: Version Identification Command
- **Req:** REQ-EN006-006
- **Procedure:** Review the documented version check command. Verify it is syntactically correct.
- **Pass:** Command is present and has correct syntax.

#### INSP-007: Documentation Style Consistency
- **Req:** REQ-EN006-024
- **Procedure:** Compare the new Upgrading section formatting against existing sections in `GETTING_STARTED.md`. Check:
  1. Platform-specific code block style (e.g., `bash`, `powershell` fenced blocks)
  2. Expected output examples present where applicable
  3. Heading hierarchy consistent with existing sections
  4. Markdown formatting (bold, code, lists) consistent
- **Pass:** Style is consistent with existing content.

#### INSP-008: SCHEMA_VERSION Constant Location
- **Req:** REQ-EN006-010
- **Procedure:** Open `statusline.py`. Search for `SCHEMA_VERSION`. Verify:
  1. Defined at module level (not inside a function)
  2. Is a string type (e.g., `SCHEMA_VERSION = "1"`)
  3. Is non-empty
- **Pass:** Constant exists at module level as a non-empty string.

#### INSP-009: Zero Dependencies Check
- **Req:** REQ-EN006-020
- **Procedure:** Review all `import` statements in `statusline.py`. Verify each is a Python stdlib module. Reference: https://docs.python.org/3.9/library/index.html
- **Pass:** All imports are stdlib modules.

#### INSP-010: Single-File Deployment Check
- **Req:** REQ-EN006-021
- **Procedure:** Verify no new `.py` files are added as runtime dependencies. The only required file is `statusline.py`.
- **Pass:** No new Python runtime files introduced.

#### INSP-011: Python 3.9 Syntax Check
- **Req:** REQ-EN006-022
- **Procedure:** Review new code in `statusline.py` for Python 3.10+ syntax:
  - No `match`/`case` statements
  - No `X | Y` union type syntax (use `Union[X, Y]` or `Optional[X]`)
  - No `(X := expr)` in unsupported contexts
  - No `str.removeprefix()` / `str.removesuffix()` (Python 3.9+, actually OK)
- **Pass:** No 3.10+ exclusive syntax found.

#### INSP-012: Function Signature Preservation
- **Req:** REQ-EN006-032
- **Procedure:** Compare function signatures of `load_config()`, `load_state()`, `save_state()`, and `deep_merge()` before and after EN-006 changes. Use `git diff` or direct inspection.
- **Pass:** All 4 signatures unchanged.

#### INSP-013: State File Additive-Only Change
- **Req:** REQ-EN006-031
- **Risk:** RISK-EN006-002, RISK-EN006-007
- **Procedure:** Review `save_state()` changes. Verify:
  1. `schema_version` is added as a new key (not replacing existing keys)
  2. Existing keys (`previous_context_tokens`, `last_compaction_from`, `last_compaction_to`) are unchanged
  3. No restructuring (e.g., no nesting under `data` key)
- **Pass:** Change is purely additive.

#### INSP-014: Warning Output Channel
- **Req:** REQ-EN006-017
- **Risk:** RISK-EN006-004
- **Procedure:** Review version checking code. Verify all warning messages use `debug_log()` (which writes to stderr when `ECW_DEBUG=1`). No `print()` or `sys.stdout.write()` for version messages.
- **Pass:** All version warnings go through `debug_log()` only.

#### INSP-015: Schema Version Documentation for Users
- **Risk:** RISK-EN006-011
- **Procedure:** If `schema_version` is mentioned in upgrade documentation, verify it states: (a) auto-managed by the script, (b) users should not set it manually, (c) purpose is internal compatibility checking.
- **Pass:** Documentation is clear and non-confusing.

#### INSP-016: No Config File Writing
- **Risk:** RISK-EN006-014
- **Procedure:** Search `statusline.py` for any code that writes to config file paths. Verify no `open(..., "w")` targeting config file paths.
- **Pass:** No config-writing code exists.

### 4.4 Analysis Procedures

#### ANALYSIS-001: Performance Impact Assessment
- **Req:** REQ-EN006-023
- **Risk:** RISK-EN006-005
- **Procedure:** Review the version checking code path. Confirm:
  1. No additional `open()` calls beyond existing config/state reads
  2. Version check is a string comparison or tuple comparison (O(1))
  3. No network calls, no disk writes, no subprocess calls for version checking
- **Pass:** Zero additional I/O. Overhead is negligible (nanoseconds).

#### ANALYSIS-002: Version Comparison Correctness
- **Risk:** RISK-EN006-001
- **Procedure:** If tuple-based comparison is used, verify:
  1. `_parse_schema_version("2.10")` produces `(2, 10)`, not a string comparison
  2. Anchored regex prevents partial matches (e.g., `"1.0abc"` is rejected)
  3. Unparseable versions return `None` and are treated as compatible (fail-open)
  If simple string equality is used, verify this is documented as the design choice.
- **Pass:** Comparison logic is correct for all expected input formats.

#### ANALYSIS-003: DEFAULT_CONFIG Behavioral Impact
- **Risk:** RISK-EN006-013
- **Procedure:** Search `statusline.py` for any code that branches on the presence or value of `schema_version` in the config dict at runtime (outside of the explicit version-checking code). Verify no existing code path is affected by the new field.
- **Pass:** No existing code references `schema_version`. Field is inert to all existing functionality.

### 4.5 Demonstration Procedures

#### DEMO-001: Version Identification Command
- **Req:** REQ-EN006-006
- **Procedure:** Execute the documented version check command against the current `statusline.py`. Verify output matches the `__version__` value in the script.
- **Pass:** Command produces correct version string (e.g., `2.1.0`).

---

## 5. Verification Schedule (Priority Order)

Verification is organized into 4 priority tiers. Higher tiers must pass before lower tiers are considered.

### Tier 1: Critical Path (P1) -- Must Pass for GREEN Light

These verifications address the highest-risk items (RISK-EN006-004, -006, -012, all score 9) and the core acceptance criteria.

| Order | Procedure | Type | Est. Time | Blocks |
|-------|-----------|------|-----------|--------|
| 1 | Full regression suite (22 existing tests) | T | 2 min | Everything |
| 2 | `run_unversioned_config_backward_compat_test` (T-004) | T | 10 sec | REQ-013, RISK-006 |
| 3 | ADDL-TEST-001: Unversioned state backward compat | T | 10 sec | REQ-014, RISK-007 |
| 4 | `run_schema_version_in_config_test` (T-001) | T | 10 sec | REQ-010, REQ-012 |
| 5 | `run_schema_version_in_state_test` (T-002) | T | 10 sec | REQ-011, REQ-031 |
| 6 | `run_schema_version_mismatch_warning_test` (T-003) | T | 10 sec | REQ-015 |
| 7 | `run_schema_version_match_no_warning_test` (T-005) | T | 10 sec | REQ-017 |
| 8 | ADDL-TEST-002: State version mismatch + reset | T | 10 sec | REQ-016 |
| 9 | ADDL-TEST-003: Stdout not polluted by version msgs | T | 20 sec | REQ-017, RISK-004 |
| 10 | `run_upgrade_docs_exist_test` (T-006) | T | 5 sec | REQ-001 |
| 11 | INSP-009: Zero dependencies | I | 2 min | REQ-020 |
| 12 | INSP-012: Function signatures unchanged | I | 2 min | REQ-032 |

### Tier 2: Important (P2) -- Required for Full Compliance

| Order | Procedure | Type | Est. Time | Blocks |
|-------|-----------|------|-----------|--------|
| 13 | ADDL-TEST-004: schema_version not overridable | T | 10 sec | REQ-018 |
| 14 | INSP-001: TOC integration | I | 2 min | REQ-001 |
| 15 | INSP-002: Platform migration commands | I | 5 min | REQ-002 |
| 16 | INSP-003: Config migration accuracy | I | 5 min | REQ-003 |
| 17 | INSP-004: State file doc accuracy | I | 3 min | REQ-004 |
| 18 | INSP-007: Documentation style | I | 5 min | REQ-024 |
| 19 | INSP-008: SCHEMA_VERSION constant location | I | 1 min | REQ-010 |
| 20 | INSP-011: Python 3.9 syntax | I | 3 min | REQ-022 |
| 21 | INSP-013: State file additive-only | I | 2 min | REQ-031, RISK-002 |
| 22 | INSP-014: Warning output channel | I | 2 min | REQ-017, RISK-004 |
| 23 | ADDL-TEST-005: Version comparison logic | T | 10 sec | RISK-001 |

### Tier 3: Supplementary (P3) -- Recommended for Completeness

| Order | Procedure | Type | Est. Time | Blocks |
|-------|-----------|------|-----------|--------|
| 24 | INSP-005: Breaking changes convention | I | 3 min | REQ-005 |
| 25 | INSP-006: Version ID command | I | 2 min | REQ-006 |
| 26 | DEMO-001: Version ID command execution | D | 1 min | REQ-006 |
| 27 | ANALYSIS-001: Performance impact | A | 5 min | REQ-023, RISK-005 |
| 28 | ANALYSIS-002: Version comparison correctness | A | 5 min | RISK-001 |
| 29 | ANALYSIS-003: DEFAULT_CONFIG behavioral impact | A | 5 min | RISK-013 |
| 30 | INSP-010: Single-file deployment | I | 1 min | REQ-021 |

### Tier 4: Defensive (Low Priority) -- Good Practice

| Order | Procedure | Type | Est. Time | Blocks |
|-------|-----------|------|-----------|--------|
| 31 | INSP-015: Schema version user documentation | I | 2 min | RISK-011 |
| 32 | INSP-016: No config file writing | I | 2 min | RISK-014 |

**Total estimated verification time:** ~70 minutes (automated tests: ~5 min; inspections: ~45 min; analysis: ~15 min; demonstration: ~5 min)

---

## 6. Scoring Guidance for Critics

This section provides scoring criteria for the adversarial critic agents to evaluate implementation quality during Phase 3 (V&V Execution).

### 6.1 Automated Test Gate

| Score | Criteria |
|-------|----------|
| **PASS** | All 22 existing tests + all 6 EN-006 tests pass. Zero regressions. |
| **CONDITIONAL PASS** | All 22 existing tests pass. 5/6 EN-006 tests pass. The failing test is a recommended additional test (ADDL-*), not a RED-phase test. |
| **FAIL** | Any existing test fails (regression). OR 2+ EN-006 RED-phase tests fail. |

### 6.2 Documentation Inspection Gate

| Score | Criteria |
|-------|----------|
| **PASS** | All 7 INSP procedures for TASK-001 (INSP-001 through INSP-007) pass. Documented behavior matches code behavior. |
| **CONDITIONAL PASS** | 5/7 INSP procedures pass. Failures are in supplementary areas (INSP-005 breaking changes convention, INSP-006 version ID command). |
| **FAIL** | INSP-002 (platform commands) or INSP-003 (config migration accuracy) fails. These are factual accuracy requirements. |

### 6.3 Code Quality Gate

| Score | Criteria |
|-------|----------|
| **PASS** | Zero dependencies preserved (INSP-009). Function signatures unchanged (INSP-012). Python 3.9 compatible (INSP-011). Single-file deployment preserved (INSP-010). Warnings go to debug_log only (INSP-014). |
| **CONDITIONAL PASS** | All above pass except one minor INSP item that does not affect functionality. |
| **FAIL** | Any of: new dependency added, function signature changed, Python 3.10+ syntax used, stdout polluted with version warnings. |

### 6.4 Risk Mitigation Gate

| Score | Criteria |
|-------|----------|
| **PASS** | All 4 YELLOW-scored risks (RISK-004, -006, -012, -013) have their mitigation verified. Residual risk scores are all GREEN. |
| **CONDITIONAL PASS** | 3/4 YELLOW risks mitigated. The unmitigated risk has a clear remediation path. |
| **FAIL** | RISK-006 (config loading conflict) is unmitigated -- this would mean existing users could be broken by the update. |

### 6.5 Overall V&V Verdict

| Verdict | Criteria |
|---------|----------|
| **GREEN (Proceed)** | All 4 gates PASS. |
| **YELLOW (Proceed with Conditions)** | At least 3 gates PASS, 1 gate CONDITIONAL PASS. No FAIL on any gate. |
| **RED (Block)** | Any gate scores FAIL. Implementation must not be merged. |

### 6.6 Acceptance Criteria Mapping

Final sign-off requires verification that all 4 acceptance criteria from EN-006-platform-expansion.md are met:

| Acceptance Criterion | Verified By | Gate |
|---------------------|-------------|------|
| Upgrade instructions in GETTING_STARTED.md | T-006 + INSP-001 through INSP-007 | Documentation Inspection |
| Schema version field in config/state files | T-001 + T-002 + INSP-008 + INSP-013 | Automated Test + Code Quality |
| Version mismatch detection with user-friendly warning | T-003 + T-005 + ADDL-TEST-002 + ADDL-TEST-003 | Automated Test |
| Backward compatibility for unversioned configs | T-004 + ADDL-TEST-001 + full regression suite | Automated Test |

---

*VCRM generated by nse-verification agent for EN-006 orchestration (en006-20260212-001)*
*Methodology: NASA NPR 7123.1D Process 7 (Technical Verification)*
