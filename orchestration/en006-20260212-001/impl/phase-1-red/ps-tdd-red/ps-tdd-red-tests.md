# EN-006 Phase 1 RED: Failing Tests Report

**Agent:** ps-tdd-red
**Enabler:** EN-006 Platform Expansion
**Date:** 2026-02-12
**Phase:** TDD RED (write failing tests BEFORE implementation)

---

## Summary

Added 6 new tests to `test_statusline.py` covering EN-006's two tasks:
- **TASK-002** (Schema Version Checking): 5 tests
- **TASK-001** (Upgrade Path Documentation): 1 test

All 5 implementation-dependent tests **FAIL** as expected (RED phase). The backward-compatibility test passes, which is correct -- it validates existing behavior that must be preserved.

---

## Test Results

| # | Test Function | Task | Result | Expected |
|---|--------------|------|--------|----------|
| 1 | `run_schema_version_in_config_test` | TASK-002 | **FAIL** | FAIL (RED) |
| 2 | `run_schema_version_in_state_test` | TASK-002 | **FAIL** | FAIL (RED) |
| 3 | `run_schema_version_mismatch_warning_test` | TASK-002 | **FAIL** | FAIL (RED) |
| 4 | `run_unversioned_config_backward_compat_test` | TASK-002 | **PASS** | PASS (validates existing backward-compat behavior) |
| 5 | `run_schema_version_match_no_warning_test` | TASK-002 | **FAIL** | FAIL (RED) |
| 6 | `run_upgrade_docs_exist_test` | TASK-001 | **FAIL** | FAIL (RED) |

**Existing tests:** All 22 existing tests continue to PASS (no regressions).

**Overall:** 22 passed, 5 failed (5 new EN-006 failures + 0 regressions)

---

## Test Details

### Test 1: `run_schema_version_in_config_test`

- **What it validates:** `DEFAULT_CONFIG` in `statusline.py` must contain a top-level `schema_version` key.
- **How it works:** Imports `DEFAULT_CONFIG` directly from `statusline.py` and checks for the key's presence.
- **Current result:** FAIL -- `DEFAULT_CONFIG` has no `schema_version` field. Output: `{"has_schema_version": false, "value": null}`.
- **To pass:** Add `"schema_version": "<version>"` to `DEFAULT_CONFIG` in `statusline.py`.

### Test 2: `run_schema_version_in_state_test`

- **What it validates:** When `save_state()` writes a state JSON file, it must include a `schema_version` field.
- **How it works:** Runs the statusline script with a configured state file path, then reads the state file and checks for `schema_version`.
- **Current result:** FAIL -- State file contains `{"previous_context_tokens": 25500, "last_compaction_from": 0, "last_compaction_to": 0}` with no `schema_version`.
- **To pass:** Modify `save_state()` to include `schema_version` in the state dict before writing.

### Test 3: `run_schema_version_mismatch_warning_test`

- **What it validates:** When the user's config has a `schema_version` that differs from the script's expected version, the output must include a version mismatch warning.
- **How it works:** Creates a config file with `"schema_version": "0.0.1"` (deliberately old), runs the script, and looks for warning text containing "version" + "mismatch"/"outdated"/"upgrade"/"warning" or the warning emoji.
- **Current result:** FAIL -- No version warning is produced. The script silently ignores the `schema_version` field.
- **To pass:** Add version comparison logic in `load_config()` or `build_status_line()` that detects mismatches and emits a warning.

### Test 4: `run_unversioned_config_backward_compat_test`

- **What it validates:** When the user's config has NO `schema_version` field (legacy/pre-EN-006 config), the script should still work without crashing and should NOT produce a mismatch warning.
- **How it works:** Creates a config with only `{"cost": {"currency_symbol": "$"}}`, runs the script, verifies it produces output without errors or mismatch warnings.
- **Current result:** PASS -- This correctly validates existing behavior. The script already handles configs without `schema_version`.
- **Note:** This test SHOULD pass even after implementation (backward compatibility preserved).

### Test 5: `run_schema_version_match_no_warning_test`

- **What it validates:** When the user's config `schema_version` matches the script's expected version, no warning should appear.
- **How it works:** First reads `DEFAULT_CONFIG.schema_version` from the script, then creates a config file with that exact version and runs the script. Verifies no warning appears.
- **Current result:** FAIL -- Cannot proceed because `DEFAULT_CONFIG` has no `schema_version` yet. Early exit with: `"DEFAULT_CONFIG has no schema_version yet (expected for RED phase)"`.
- **To pass:** Once `DEFAULT_CONFIG` has `schema_version`, this test will create a matching config and verify no warning is emitted.

### Test 6: `run_upgrade_docs_exist_test`

- **What it validates:** `GETTING_STARTED.md` must contain a markdown heading (h1-h3) with "Upgrade", "Migration", "Upgrading", or "Migrating" in the text.
- **How it works:** Reads `GETTING_STARTED.md` and searches for headings matching the pattern `^#{1,3}\s+.*(?:Upgrade|Migration|Upgrading|Migrating).*$`.
- **Current result:** FAIL -- No such heading exists. Current GETTING_STARTED.md has sections for Installation, Verification, Configuration, Troubleshooting, etc., but nothing about upgrading.
- **To pass:** Add an "Upgrade" or "Migration" section to `GETTING_STARTED.md`.

---

## Observations About Current Codebase

### DEFAULT_CONFIG Structure

The `DEFAULT_CONFIG` dict in `statusline.py` (line 62-161) is a nested dict with top-level keys: `display`, `segments`, `context`, `cost`, `tokens`, `session`, `compaction`, `tools`, `git`, `directory`, `colors`, `advanced`. There is no versioning mechanism at all.

### State File Structure

The `save_state()` function (line 284) writes a dict with exactly three keys: `previous_context_tokens`, `last_compaction_from`, `last_compaction_to`. Adding `schema_version` here is straightforward.

### Config Loading

`load_config()` (line 184) does a `deep_merge()` of user config over DEFAULT_CONFIG. A `schema_version` in the user config would overwrite the default. This means version checking must happen AFTER merge, comparing the user-provided version against the expected version, not the merged result.

### Recommended Implementation Approach

1. Add `"schema_version": "2.2.0"` (or similar) to `DEFAULT_CONFIG`
2. In `load_config()`, before merging, extract `user_config.get("schema_version")` and compare against `DEFAULT_CONFIG["schema_version"]`
3. If mismatched, set a flag or store a warning message that `build_status_line()` can include in output
4. If absent from user config, treat as v1.0 (backward compat, no warning)
5. In `save_state()`, add `schema_version` to the state dict
6. Add Upgrade/Migration section to `GETTING_STARTED.md`

### GETTING_STARTED.md Structure

The doc currently has sections up through "Uninstallation" and a "Quick Reference Card". An "Upgrade" section should be inserted in the Table of Contents (around position 13-14) and as a full section before or after "Uninstallation".

---

## Files Modified

- `test_statusline.py`: Added 6 new test functions and registered them in `main()` under the `# EN-006` section marker.

## Next Phase

The **GREEN** phase implementer (`ps-tdd-green`) should:
1. Add `schema_version` to `DEFAULT_CONFIG` in `statusline.py`
2. Add version checking logic to `load_config()` and warning output to `build_status_line()`
3. Add `schema_version` to state dict in `save_state()` and `load_state()`
4. Add Upgrade/Migration section to `GETTING_STARTED.md`
5. Run `uv run python test_statusline.py` and confirm all 28 tests pass (GREEN)
