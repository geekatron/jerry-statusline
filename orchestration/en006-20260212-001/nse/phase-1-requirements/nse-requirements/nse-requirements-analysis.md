# EN-006 Requirements Analysis

> **Document ID:** NSE-REQ-EN006-001
> **Version:** 1.0
> **Date:** 2026-02-12
> **Author:** nse-requirements agent
> **Status:** DRAFT
> **Orchestration:** en006-20260212-001
> **Method:** NASA NPR 7123.1D (Technical Requirements Definition)

---

## 1. Scope

This requirements analysis covers EN-006 (Platform Expansion), which addresses two objectives within the ECW Status Line project:

1. **TASK-001:** Add upgrade path documentation to `GETTING_STARTED.md` covering version migration, config file migration, state file compatibility, and breaking changes.
2. **TASK-002:** Add schema version checking to the `statusline.py` script to detect config/state format mismatches, provide user-friendly warnings, and maintain backward compatibility with unversioned files.

### 1.1 System Context

ECW Status Line is a single-file Python 3.9+ script (`statusline.py`) that reads JSON from stdin (provided by Claude Code's `statusLine` hook) and outputs a formatted status line to stdout. It uses zero external dependencies (stdlib only).

The system manages two persistent file types:
- **Configuration file:** `ecw-statusline-config.json` -- user-defined overrides merged into `DEFAULT_CONFIG`
- **State file:** `ecw-statusline-state.json` -- compaction detection state (previous token counts)

Both files are optional. The script operates correctly when neither exists.

### 1.2 Current Version

- Script version: `2.1.0` (as defined in `__version__` and the module docstring)
- Config schema: Implicit (no version field; structure defined by `DEFAULT_CONFIG` dict)
- State schema: Implicit (no version field; structure defined by `load_state()` default dict)

---

## 2. Applicable Documents

| ID | Document | Relevance |
|----|----------|-----------|
| AD-001 | `statusline.py` (v2.1.0) | Primary source code; contains `DEFAULT_CONFIG`, `load_config()`, `load_state()`, `save_state()` |
| AD-002 | `test_statusline.py` (v2.1.0) | Test suite; 21 functional tests covering normal, warning, critical, and edge cases |
| AD-003 | `GETTING_STARTED.md` | Current user documentation; installation, configuration, troubleshooting |
| AD-004 | `EN-006-platform-expansion.md` | Work item definition with acceptance criteria |
| AD-005 | `WORKTRACKER.md` | Project-level tracking and progress |
| AD-006 | `CLAUDE.md` | Project conventions (uv required, code style, testing rules) |

---

## 3. Functional Requirements

### 3.1 TASK-001: Upgrade Path Documentation

These requirements define what documentation content SHALL be added to `GETTING_STARTED.md`.

#### REQ-EN006-001: Upgrade Section in GETTING_STARTED.md

**The documentation SHALL include a new "Upgrading" section** in `GETTING_STARTED.md` that is linked from the Table of Contents and positioned between the "Uninstallation" section and "Next Steps" section (or at an equivalently discoverable location).

- **Rationale:** Gap G-022 identifies the absence of upgrade path documentation. Users currently have no guidance on how to move from one version to another.
- **Verification:** Manual inspection of `GETTING_STARTED.md` confirms the section exists and is reachable from the TOC.

#### REQ-EN006-002: Version Migration Instructions

**The upgrade section SHALL include step-by-step instructions for replacing the `statusline.py` script file** on each supported platform (macOS, Windows, Linux), covering:
1. Downloading or copying the new version of `statusline.py`
2. Verifying the new version runs correctly (same verification command as installation)
3. Preserving the existing configuration file (`ecw-statusline-config.json`)

- **Rationale:** The single-file deployment model means upgrades are file replacements. Users need explicit commands.
- **Verification:** The documented commands are syntactically correct and consistent with existing installation instructions.

#### REQ-EN006-003: Configuration File Migration Guidance

**The upgrade section SHALL document how configuration files interact with new versions**, including:
1. Statement that user config files are preserved during upgrades (they are separate from `statusline.py`)
2. Guidance on what happens when new config keys are added in a new version (they use defaults via `deep_merge`)
3. Guidance on what happens when config keys are removed or renamed in a new version (the old keys are silently ignored by `deep_merge`)

- **Rationale:** Users need to understand that their `ecw-statusline-config.json` is safe across upgrades and that new defaults are automatically applied.
- **Verification:** The documented behavior matches the actual behavior of `load_config()` and `deep_merge()`.

#### REQ-EN006-004: State File Compatibility Guidance

**The upgrade section SHALL document state file (`ecw-statusline-state.json`) behavior across versions**, including:
1. Statement that the state file is automatically managed and does not require manual intervention
2. Guidance that if the state file format changes, the script will fall back to defaults (per existing `load_state()` error handling)
3. Instruction that users MAY safely delete the state file if they experience issues after an upgrade

- **Rationale:** The state file is an implementation detail that users should not need to manage, but they should know it exists and what to do if it causes problems.
- **Verification:** The documented behavior matches `load_state()` which returns a default dict on any parse error.

#### REQ-EN006-005: Breaking Changes Documentation

**The upgrade section SHALL include a "Breaking Changes" subsection** that:
1. Documents the current version's breaking changes (if any) from previous versions
2. Establishes a convention for documenting breaking changes in future versions
3. Lists the types of changes that would constitute a breaking change (removed config keys, changed default behavior, changed output format)

- **Rationale:** Users need to know what could break their workflows when upgrading, and maintainers need a convention for documenting this.
- **Verification:** The subsection exists and the listed categories are comprehensive relative to the script's interface surface.

#### REQ-EN006-006: Version Identification Command

**The upgrade section SHALL document how users can check their current installed version**, including:
1. A command to extract the version from the installed script (e.g., grepping `__version__`)
2. Expected output format

- **Rationale:** Users need to know what version they are currently running before deciding whether to upgrade.
- **Verification:** The documented command works against the current `statusline.py` and produces the correct version string.

### 3.2 TASK-002: Schema Version Checking

These requirements define what code changes SHALL be made to `statusline.py` and `test_statusline.py`.

#### REQ-EN006-010: Schema Version Constant

**The script SHALL define a `SCHEMA_VERSION` constant** (as a string, e.g., `"1"`) that represents the current version of the config and state file schemas.

- **Rationale:** A version identifier is necessary for mismatch detection. Using a simple integer string (not semver) is appropriate given the small, single-file scope.
- **Verification:** The constant exists in `statusline.py` and is a non-empty string.

#### REQ-EN006-011: Schema Version in State File

**The `save_state()` function SHALL include a `"schema_version"` field** in the state JSON it writes, set to the current `SCHEMA_VERSION` value.

- **Rationale:** State files need to be identifiable by version so that future schema changes can be detected.
- **Verification:** After running the script, the state file JSON contains a `"schema_version"` key with the correct value.

#### REQ-EN006-012: Schema Version in Default Config

**The `DEFAULT_CONFIG` dictionary SHALL include a top-level `"schema_version"` field** set to the current `SCHEMA_VERSION` value.

- **Rationale:** Config files need a version field so that user config files can be checked against the expected schema. The field in `DEFAULT_CONFIG` serves as the authoritative reference.
- **Verification:** `DEFAULT_CONFIG["schema_version"]` exists and equals `SCHEMA_VERSION`.

#### REQ-EN006-013: Backward Compatibility for Unversioned Config Files

**The `load_config()` function SHALL treat config files without a `"schema_version"` field as valid** and SHALL NOT emit any warning or error for such files.

- **Rationale:** Existing users have config files without a `schema_version` field. These must continue to work without any change or user action. Per acceptance criteria: "Backward compatibility for unversioned configs."
- **Verification:** A test confirms that a config file without `"schema_version"` loads without warnings when `ECW_DEBUG=1`.

#### REQ-EN006-014: Backward Compatibility for Unversioned State Files

**The `load_state()` function SHALL treat state files without a `"schema_version"` field as valid** and SHALL NOT emit any warning or error for such files. The missing field SHALL be treated as equivalent to the current schema version.

- **Rationale:** Existing state files lack the `schema_version` field. The script must not break for users who upgrade without deleting their state file.
- **Verification:** A test confirms that a state file without `"schema_version"` loads without error and the script produces normal output.

#### REQ-EN006-015: Version Mismatch Detection for Config Files

**When `load_config()` reads a user config file that contains a `"schema_version"` field whose value differs from the current `SCHEMA_VERSION`, it SHALL emit a user-friendly warning** via `debug_log()`.

- **Rationale:** Users who have explicitly versioned config files should be warned when the script's expected schema has changed, so they can review their config for compatibility.
- **Verification:** A test confirms that a config file with a mismatched `"schema_version"` triggers a debug log message containing the words "schema" and "version" (or similar identifiable text).

#### REQ-EN006-016: Version Mismatch Detection for State Files

**When `load_state()` reads a state file that contains a `"schema_version"` field whose value differs from the current `SCHEMA_VERSION`, it SHALL emit a user-friendly warning** via `debug_log()` and SHALL reset the state to defaults (re-initialize).

- **Rationale:** A state file with a mismatched schema version may contain incompatible data structures. The safest behavior is to start fresh, which only loses compaction detection history (a low-impact data loss).
- **Verification:** A test confirms that a state file with a mismatched `"schema_version"` causes the script to use default state values and logs a debug warning.

#### REQ-EN006-017: No Impact on Normal Output

**Schema version checking SHALL NOT alter the status line output** under any condition (version match, version mismatch, missing version). All version-related messages SHALL be emitted only via `debug_log()` (to stderr, only when `ECW_DEBUG=1`).

- **Rationale:** The status line is a display-critical path. Version warnings must not pollute the output that Claude Code reads.
- **Verification:** Tests confirm that stdout output is identical with and without schema version fields in config/state files when `ECW_DEBUG` is not set.

#### REQ-EN006-018: Schema Version Field Excluded from Deep Merge Override

**The `schema_version` field in `DEFAULT_CONFIG` SHALL NOT be overridable by user config files.** If a user config file contains `"schema_version"`, it SHALL be used only for mismatch detection, not to change the running schema version.

- **Rationale:** The schema version is an internal identifier, not a user-configurable setting. Allowing users to override it would defeat the purpose of mismatch detection.
- **Verification:** A test confirms that after loading a config with a different `schema_version`, the effective config's `schema_version` matches `SCHEMA_VERSION`, not the user-supplied value.

---

## 4. Non-Functional Requirements

#### REQ-EN006-020: Zero Dependencies Preserved

**All changes SHALL maintain the zero-dependency constraint** (Python 3.9+ stdlib only). No new imports or external packages SHALL be introduced.

- **Verification:** `statusline.py` contains no imports outside the Python standard library after changes.

#### REQ-EN006-021: Single-File Deployment Preserved

**All code changes SHALL remain within `statusline.py`.** No additional Python files SHALL be introduced as runtime dependencies.

- **Verification:** The script runs correctly when only `statusline.py` is present (no other custom Python files).

#### REQ-EN006-022: Python 3.9 Compatibility

**All code changes SHALL be compatible with Python 3.9+.** No syntax or API features exclusive to Python 3.10+ SHALL be used (e.g., no `match` statements, no `int | str` union syntax).

- **Verification:** CI runs tests on Python 3.9 and they pass.

#### REQ-EN006-023: Performance Impact

**Schema version checking SHALL add negligible overhead** to the script's execution time. The check is a simple string comparison and SHALL NOT involve file I/O beyond what `load_config()` and `load_state()` already perform.

- **Verification:** No additional file reads or writes are introduced beyond those already performed by existing functions.

#### REQ-EN006-024: Documentation Clarity

**All documentation additions SHALL follow the existing style and conventions** of `GETTING_STARTED.md`, including:
1. Platform-specific command blocks (macOS, Windows, Linux)
2. "Expected output" examples where applicable
3. Troubleshooting-style Q&A format for common issues
4. Markdown formatting consistent with existing sections

- **Verification:** Manual inspection confirms style consistency.

---

## 5. Interface Requirements

#### REQ-EN006-030: Config File Interface (ecw-statusline-config.json)

**The config file JSON schema SHALL be extended with an optional top-level `"schema_version"` field** (string type).

Current interface:
```json
{
  "display": { ... },
  "segments": { ... },
  "context": { ... },
  "cost": { ... },
  "tokens": { ... },
  "session": { ... },
  "compaction": { ... },
  "tools": { ... },
  "git": { ... },
  "directory": { ... },
  "colors": { ... },
  "advanced": { ... }
}
```

Extended interface:
```json
{
  "schema_version": "1",
  "display": { ... },
  ...
}
```

- **Backward compatibility:** Files without `"schema_version"` SHALL continue to load without error (REQ-EN006-013).
- **Forward compatibility:** Unrecognized keys in config are already silently ignored by `deep_merge()`.

#### REQ-EN006-031: State File Interface (ecw-statusline-state.json)

**The state file JSON schema SHALL be extended with a `"schema_version"` field** (string type).

Current interface:
```json
{
  "previous_context_tokens": 0,
  "last_compaction_from": 0,
  "last_compaction_to": 0
}
```

Extended interface:
```json
{
  "schema_version": "1",
  "previous_context_tokens": 0,
  "last_compaction_from": 0,
  "last_compaction_to": 0
}
```

- **Backward compatibility:** State files without `"schema_version"` SHALL continue to load without error (REQ-EN006-014).

#### REQ-EN006-032: Existing Function Signatures

**The following function signatures SHALL NOT change:**
- `load_config() -> Dict[str, Any]`
- `load_state(config: Dict) -> Dict[str, Any]`
- `save_state(config: Dict, state: Dict[str, Any]) -> None`
- `deep_merge(base: Dict, override: Dict) -> Dict`

**Rationale:** These are the primary interfaces between subsystems. Signature changes would break the internal contract.

#### REQ-EN006-033: Stdin/Stdout Interface Unchanged

**The stdin JSON input schema and the stdout status line output format SHALL NOT be modified.** Schema version checking is purely an internal concern affecting config/state files.

---

## 6. Constraints

| ID | Constraint | Impact |
|----|-----------|--------|
| C-001 | Single-file deployment (`statusline.py` only) | All code changes must be in one file |
| C-002 | Zero external dependencies (stdlib only) | Cannot use semver libraries, TOML parsers, etc. |
| C-003 | Python 3.9+ compatibility | No match statements, no `X \| Y` union syntax |
| C-004 | Backward compatibility with existing config/state files | Cannot require users to modify or delete existing files |
| C-005 | Debug-only warnings (no stdout pollution) | All schema warnings go to stderr via `debug_log()` only |
| C-006 | `uv` required for all Python operations | Tests run as `uv run python test_statusline.py` |
| C-007 | Conventional commits for git messages | `feat:`, `fix:`, `docs:` prefixes required |
| C-008 | Max line length 100 characters | Enforced by ruff |
| C-009 | Type hints required for all functions | Enforced by project conventions |

---

## 7. Traceability Matrix

| Requirement | Gap | Acceptance Criteria | Task |
|-------------|-----|---------------------|------|
| REQ-EN006-001 | G-022 | Upgrade instructions in GETTING_STARTED.md | TASK-001 |
| REQ-EN006-002 | G-022 | Upgrade instructions in GETTING_STARTED.md | TASK-001 |
| REQ-EN006-003 | G-022 | Upgrade instructions in GETTING_STARTED.md | TASK-001 |
| REQ-EN006-004 | G-022 | Upgrade instructions in GETTING_STARTED.md | TASK-001 |
| REQ-EN006-005 | G-022 | Upgrade instructions in GETTING_STARTED.md | TASK-001 |
| REQ-EN006-006 | G-022 | Upgrade instructions in GETTING_STARTED.md | TASK-001 |
| REQ-EN006-010 | -- | Schema version field in config/state files | TASK-002 |
| REQ-EN006-011 | -- | Schema version field in config/state files | TASK-002 |
| REQ-EN006-012 | -- | Schema version field in config/state files | TASK-002 |
| REQ-EN006-013 | -- | Backward compatibility for unversioned configs | TASK-002 |
| REQ-EN006-014 | -- | Backward compatibility for unversioned configs | TASK-002 |
| REQ-EN006-015 | -- | Version mismatch detection with user-friendly warning | TASK-002 |
| REQ-EN006-016 | -- | Version mismatch detection with user-friendly warning | TASK-002 |
| REQ-EN006-017 | -- | Version mismatch detection with user-friendly warning | TASK-002 |
| REQ-EN006-018 | -- | Schema version field in config/state files | TASK-002 |
| REQ-EN006-020 | -- | (Project constraint) | TASK-002 |
| REQ-EN006-021 | -- | (Project constraint) | TASK-002 |
| REQ-EN006-022 | -- | (Project constraint) | TASK-002 |
| REQ-EN006-023 | -- | (Project constraint) | TASK-002 |
| REQ-EN006-024 | G-022 | Upgrade instructions in GETTING_STARTED.md | TASK-001 |
| REQ-EN006-030 | -- | Schema version field in config/state files | TASK-002 |
| REQ-EN006-031 | -- | Schema version field in config/state files | TASK-002 |
| REQ-EN006-032 | -- | (Stability constraint) | TASK-002 |
| REQ-EN006-033 | -- | (Stability constraint) | TASK-002 |

---

## 8. Risk Considerations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Users confused by schema version warnings | Low | Low | Warnings only in debug mode (REQ-EN006-017) |
| Old state files cause unexpected behavior after upgrade | Low | Low | State reset on mismatch (REQ-EN006-016) |
| Schema version field conflicts with user config keys | Very Low | Low | Top-level `schema_version` is an unlikely user key |
| Documentation becomes stale if upgrade process changes | Medium | Medium | Establish convention for maintaining upgrade docs (REQ-EN006-005) |

---

## 9. Open Questions

| # | Question | Status | Resolution |
|---|----------|--------|------------|
| OQ-1 | Should `schema_version` use integer strings ("1", "2") or semver ("1.0.0")? | RECOMMENDED: Integer strings | Simpler comparison, appropriate for scope |
| OQ-2 | Should config schema version and state schema version be tracked independently? | RECOMMENDED: Single shared version | Both schemas are simple and change together in this single-file project |
| OQ-3 | Should the upgrade section include a changelog or link to releases? | RECOMMENDED: Link to GitHub releases | Avoids maintaining duplicate changelog in docs |

---

## Appendix A: Current Code Analysis

### A.1 DEFAULT_CONFIG Structure (statusline.py, lines 62-161)

The config is a nested dict with 12 top-level keys: `display`, `segments`, `context`, `cost`, `tokens`, `session`, `compaction`, `tools`, `git`, `directory`, `colors`, `advanced`. Adding `schema_version` as a 13th top-level key is structurally consistent.

### A.2 load_config() Behavior (statusline.py, lines 184-199)

1. Deep-copies `DEFAULT_CONFIG`
2. Searches `CONFIG_PATHS` for a config file
3. If found, loads JSON and deep-merges into the copy
4. Returns merged config

**Schema version insertion point:** After `deep_merge`, restore `schema_version` from `DEFAULT_CONFIG` (not user override) per REQ-EN006-018.

### A.3 load_state() Behavior (statusline.py, lines 262-281)

1. Resolves state file path
2. If file exists, loads JSON
3. On any error, returns default dict
4. Default dict has 3 keys: `previous_context_tokens`, `last_compaction_from`, `last_compaction_to`

**Schema version insertion point:** After loading, check `schema_version` field. If missing, treat as current. If mismatched, log warning and return defaults. Per REQ-EN006-016.

### A.4 save_state() Behavior (statusline.py, lines 284-319)

Uses atomic write pattern (temp file + `os.replace`). The `schema_version` field should be injected into the state dict before serialization per REQ-EN006-011.

### A.5 GETTING_STARTED.md Structure (1176 lines)

Current TOC has 13 sections. The "Upgrading" section should be added as section 14 (before or after "Uninstallation") and linked from the TOC per REQ-EN006-001.

---

*End of requirements analysis.*
