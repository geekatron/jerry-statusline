DISCLAIMER: This guidance is AI-generated based on NASA Systems Engineering
standards. It is advisory only and does not constitute official NASA guidance.
All SE decisions require human review and professional engineering judgment.

---

# EN-005 Verification Cross-Reference Matrix (VCRM) and Test Plan

**Document ID:** NSE-VCRM-EN005-001
**Version:** 1.0
**Date:** 2026-02-12
**Author:** nse-verification agent (AI-generated)
**Process Reference:** NPR 7123.1D Process 7 -- Verification and Validation
**Workflow:** en005-20260211-001
**Status:** DRAFT -- Requires human review

---

## L0: V&V Summary

### Verification Strategy Overview

This Verification Cross-Reference Matrix (VCRM) establishes full bidirectional traceability between the 15 formal requirements defined in NSE-REQ-EN005-001 and their corresponding verification activities. The verification strategy employs two primary methods:

1. **Test (Automated):** Functional requirements are verified through automated subprocess-based tests in `test_statusline.py`. Each test invokes `statusline.py` in an isolated subprocess with controlled environment variables and configuration files, then asserts specific output characteristics. This approach ensures process-level isolation and eliminates import-time caching concerns.

2. **Inspection (Manual):** Documentation requirements and certain code-structural requirements are verified through structured code/document review with explicit checklists. Inspections target `statusline.py` (for code-structural checks) and `GETTING_STARTED.md` (for documentation completeness).

### Coverage Metrics

| Metric | Value |
|--------|-------|
| Total requirements | 15 |
| Requirements verified by Test | 10 |
| Requirements verified by Inspection | 6 |
| Requirements with dual verification (Test + Inspection) | 1 (REQ-EN005-004) |
| Automated test procedures | 8 (5 new + 3 existing) |
| Inspection procedures | 6 |
| Total verification activities | 14 |
| Bidirectional traceability coverage | 100% (15/15) |

**Note:** REQ-EN005-004 is verified by both Inspection (code review of DEFAULT_CONFIG) and indirectly by Test (the use_color disabled test proves the config key exists and functions). It is counted once in each method column.

### Pass/Fail Criteria

The EN-005 V&V effort is PASSED when ALL of the following hold:

1. **Automated tests:** All 20+ tests in `test_statusline.py` pass with exit code 0 (17 existing + 3 EN-005 RED-phase + expected GREEN-phase additions).
2. **Regression:** Zero existing tests regress (i.e., all 17 pre-EN-005 tests continue to pass unchanged).
3. **Inspections:** All 6 inspection checklists are completed with all items marked PASS.
4. **Risk mitigations:** All 4 YELLOW-risk mitigations are confirmed implemented per the risk-to-verification mapping.

The EN-005 V&V effort is FAILED if any single verification activity produces a FAIL result.

---

## L1: Verification Cross-Reference Matrix

### Master Traceability Table

| Req ID | Title | Type | Verification Method | Test/Procedure ID | Pass Criteria | Status | Evidence Reference |
|--------|-------|------|-------------------|-------------------|---------------|--------|--------------------|
| REQ-EN005-001 | NO_COLOR disables all ANSI output | Functional | Test | VT-EN005-001 | Output contains 0 ANSI escape sequences (`\x1b\[`) when `NO_COLOR=1` is set in environment | PLANNED | `test_statusline.py::run_no_color_env_test()` |
| REQ-EN005-002 | NO_COLOR precedence over config | Functional | Test | VT-EN005-002 | Output contains 0 ANSI escape sequences when `NO_COLOR=1` AND `use_color: true` in config | PLANNED | `test_statusline.py::run_color_matrix_test()` scenario 2 |
| REQ-EN005-003 | NO_COLOR standard compliance (presence check) | Functional | Test | VT-EN005-003 | Output contains 0 ANSI escape sequences for `NO_COLOR=""`, `NO_COLOR=0`, and `NO_COLOR=1` (all presence-based) | PLANNED | `test_statusline.py::run_color_matrix_test()` scenarios 2, 4 + VT-EN005-001 |
| REQ-EN005-004 | use_color config toggle, default true | Functional | Inspection + Test | VI-EN005-001, VT-EN005-004 | `DEFAULT_CONFIG["display"]["use_color"]` exists with value `True`; default behavior produces ANSI codes | PLANNED | `statusline.py` code review + `test_statusline.py::run_color_matrix_test()` scenario 1 |
| REQ-EN005-005 | use_color=false disables ANSI codes | Functional | Test | VT-EN005-005 | Output contains 0 ANSI escape sequences when config `display.use_color` is `false` and `NO_COLOR` is absent | PLANNED | `test_statusline.py::run_use_color_disabled_test()` |
| REQ-EN005-006 | use_color independent of use_emoji | Functional | Test | VT-EN005-006 | With `use_color: false, use_emoji: true`: output has emoji characters but 0 ANSI escape sequences; with `use_color: true, use_emoji: false`: output has ANSI codes but 0 non-ASCII emoji characters | PLANNED | `test_statusline.py::run_color_matrix_test()` + independence assertion |
| REQ-EN005-007 | Atomic state writes (temp + rename) | Functional | Test | VT-EN005-007 | `save_state()` uses temp file in same directory + `os.replace()` pattern; state file is valid JSON after write; no orphan temp files remain | PLANNED | `test_statusline.py::run_atomic_write_test()` (to be added in GREEN phase) |
| REQ-EN005-008 | Atomic write graceful degradation | Functional | Test | VT-EN005-008 | Script produces valid output with exit code 0 when state file location is read-only; no temp files orphaned on failure | PLANNED | `test_statusline.py::run_readonly_state_test()` (existing) |
| REQ-EN005-009 | Preserve error handling contract | Functional | Test | VT-EN005-009 | All 4 existing tests exercising `save_state()` pass without modification: `run_compaction_test()`, `run_readonly_state_test()`, `run_no_home_test()`, `run_corrupt_state_test()` | PLANNED | `test_statusline.py` (existing regression tests) |
| REQ-EN005-010 | git_timeout configurable | Functional | Test | VT-EN005-010 | When config `advanced.git_timeout` is set to a custom value (e.g., 10), the configured value is used by `get_git_info()` (verifiable via `ECW_DEBUG=1` log output) | PLANNED | `test_statusline.py::run_git_timeout_config_test()` (to be added in GREEN phase) |
| REQ-EN005-011 | git_timeout documented | Documentation | Inspection | VI-EN005-002 | `GETTING_STARTED.md` contains `advanced.git_timeout` in configuration table with default value, description, and usage example | PLANNED | `GETTING_STARTED.md` review |
| REQ-EN005-012 | UNC path limitations documented | Documentation | Inspection | VI-EN005-003 | `GETTING_STARTED.md` contains UNC path section documenting: (1) `Path.home()` behavior, (2) state file write limitations, (3) git operation considerations, (4) performance notes | PLANNED | `GETTING_STARTED.md` review |
| REQ-EN005-013 | UNC alternatives documented | Documentation | Inspection | VI-EN005-004 | `GETTING_STARTED.md` UNC section includes 3 alternatives: (1) mapped drive letter, (2) WSL 2, (3) local clone | PLANNED | `GETTING_STARTED.md` review |
| REQ-EN005-014 | SSH requirements documented | Documentation | Inspection | VI-EN005-005 | `GETTING_STARTED.md` contains SSH section with: (1) TERM variable requirements, (2) locale/encoding requirements, (3) emoji rendering note, (4) NO_COLOR fallback advice | PLANNED | `GETTING_STARTED.md` review |
| REQ-EN005-015 | tmux configuration documented | Documentation | Inspection | VI-EN005-006 | `GETTING_STARTED.md` contains tmux section with: (1) `tmux.conf` settings for 256-color, (2) `default-terminal` recommendation, (3) progress bar rendering note, (4) verification command | PLANNED | `GETTING_STARTED.md` review |

---

## L1: Test Procedures

### Automated Test Procedures

---

#### VT-EN005-001: NO_COLOR Environment Variable Disables ANSI

| Attribute | Value |
|-----------|-------|
| **Test ID** | VT-EN005-001 |
| **Requirement(s)** | REQ-EN005-001, REQ-EN005-003 |
| **Risk Mitigation** | RSK-EN005-001 (YELLOW 9), RSK-EN005-010 (YELLOW 6) |
| **Priority** | 1 (YELLOW risk mitigation) |
| **Test Function** | `run_no_color_env_test()` |
| **Source File** | `test_statusline.py` lines 804-855 |
| **Status** | RED (test written, implementation pending) |

**Setup:**
1. Copy current process environment: `env = os.environ.copy()`
2. Set `env["PYTHONUTF8"] = "1"` for Windows UTF-8 compatibility
3. Set `env["NO_COLOR"] = "1"` to trigger NO_COLOR behavior

**Steps:**
1. Invoke `subprocess.run([sys.executable, str(STATUSLINE_SCRIPT)], input=json.dumps(PAYLOAD_NORMAL), env=env, capture_output=True, text=True, timeout=5)`
2. Compile ANSI detection regex: `re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")`
3. Search stdout for ANSI escape sequences
4. Verify stdout is non-empty

**Expected Result:**
- Exit code: 0
- ANSI sequence count in stdout: 0
- stdout length: > 0 characters (output is produced)

**Cleanup:**
- None required (env vars are subprocess-scoped)

---

#### VT-EN005-002: NO_COLOR Precedence Over use_color Config

| Attribute | Value |
|-----------|-------|
| **Test ID** | VT-EN005-002 |
| **Requirement(s)** | REQ-EN005-002 |
| **Risk Mitigation** | RSK-EN005-001 (YELLOW 9) |
| **Priority** | 1 (YELLOW risk mitigation) |
| **Test Function** | `run_color_matrix_test()` scenario 2 |
| **Source File** | `test_statusline.py` lines 922-1018 |
| **Status** | RED (test written, implementation pending) |

**Setup:**
1. Copy current process environment
2. Set `env["NO_COLOR"] = "1"`
3. Write config file `ecw-statusline-config.json` with `{"display": {"use_color": true}}` to script directory

**Steps:**
1. Invoke statusline.py via subprocess with the environment and config
2. Search stdout for ANSI escape sequences using regex `\x1b\[[0-9;]*[a-zA-Z]`
3. Verify output is non-empty

**Expected Result:**
- Exit code: 0
- ANSI sequence count: 0 (NO_COLOR overrides use_color: true)
- stdout length: > 0

**Cleanup:**
- Remove `ecw-statusline-config.json` in `finally` block

---

#### VT-EN005-003: NO_COLOR Presence Check (Empty String, Zero, One)

| Attribute | Value |
|-----------|-------|
| **Test ID** | VT-EN005-003 |
| **Requirement(s)** | REQ-EN005-003 |
| **Risk Mitigation** | RSK-EN005-010 (YELLOW 6) |
| **Priority** | 1 (YELLOW risk mitigation) |
| **Test Function** | `run_color_matrix_test()` scenarios 2, 4 + supplementary empty-string check |
| **Source File** | `test_statusline.py` lines 922-1018 |
| **Status** | RED (test written; empty-string sub-case may need enhancement in GREEN phase) |

**Setup (per sub-case):**
1. Copy current process environment
2. Set `env["NO_COLOR"]` to one of: `"1"`, `"0"`, `""` (empty string)
3. No config file (use defaults)

**Steps (per sub-case):**
1. Invoke statusline.py via subprocess
2. Search stdout for ANSI escape sequences

**Expected Result (all sub-cases):**
- Exit code: 0
- ANSI sequence count: 0 for ALL values (`""`, `"0"`, `"1"`)
- This validates presence-based checking (`"NO_COLOR" in os.environ`), not value-based

**Implementation Note:** The current `run_color_matrix_test()` uses `NO_COLOR=1` in scenarios 2 and 4. For full REQ-EN005-003 compliance, the GREEN phase should add explicit sub-cases for `NO_COLOR=""` and `NO_COLOR=0`. This is recommended but not blocking if scenarios 2 and 4 pass, combined with code inspection confirming `is not None` usage.

**Cleanup:**
- Remove config file in `finally` block

---

#### VT-EN005-004: use_color Default Value (True)

| Attribute | Value |
|-----------|-------|
| **Test ID** | VT-EN005-004 |
| **Requirement(s)** | REQ-EN005-004 |
| **Risk Mitigation** | RSK-EN005-009 (GREEN 4) |
| **Priority** | 2 (GREEN risk) |
| **Test Function** | `run_color_matrix_test()` scenario 1 |
| **Source File** | `test_statusline.py` lines 922-1018 |
| **Status** | RED (test written, implementation pending) |

**Setup:**
1. Copy current process environment
2. Remove `NO_COLOR` from env: `env.pop("NO_COLOR", None)`
3. Write config file with `{"display": {"use_color": true}}`

**Steps:**
1. Invoke statusline.py via subprocess
2. Search stdout for ANSI escape sequences

**Expected Result:**
- Exit code: 0
- ANSI sequence count: > 0 (colors ARE present with default/true use_color)
- stdout length: > 0

**Cleanup:**
- Remove config file in `finally` block

---

#### VT-EN005-005: use_color=false Disables ANSI Codes

| Attribute | Value |
|-----------|-------|
| **Test ID** | VT-EN005-005 |
| **Requirement(s)** | REQ-EN005-005 |
| **Risk Mitigation** | RSK-EN005-002 (YELLOW 6) |
| **Priority** | 1 (YELLOW risk mitigation) |
| **Test Function** | `run_use_color_disabled_test()` |
| **Source File** | `test_statusline.py` lines 858-919 |
| **Status** | RED (test written, implementation pending) |

**Setup:**
1. Copy current process environment
2. Remove `NO_COLOR` from env: `env.pop("NO_COLOR", None)` (isolate config effect)
3. Write config file with `{"display": {"use_color": false}}`

**Steps:**
1. Invoke statusline.py via subprocess
2. Search stdout for ANSI escape sequences using regex

**Expected Result:**
- Exit code: 0
- ANSI sequence count: 0
- stdout length: > 0

**Cleanup:**
- Remove `ecw-statusline-config.json` in `finally` block

---

#### VT-EN005-006: use_color Independent of use_emoji

| Attribute | Value |
|-----------|-------|
| **Test ID** | VT-EN005-006 |
| **Requirement(s)** | REQ-EN005-006 |
| **Risk Mitigation** | RSK-EN005-001 (YELLOW 9) |
| **Priority** | 1 (YELLOW risk mitigation) |
| **Test Function** | `run_color_matrix_test()` + independence assertion |
| **Source File** | `test_statusline.py` lines 922-1018 (matrix covers partial; full independence requires supplementary assertion) |
| **Status** | RED (partial coverage via matrix; explicit independence test recommended for GREEN phase) |

**Setup (sub-case A: color off, emoji on):**
1. Write config: `{"display": {"use_color": false, "use_emoji": true}}`
2. Remove `NO_COLOR` from env

**Steps (sub-case A):**
1. Invoke statusline.py via subprocess
2. Search stdout for ANSI escape sequences (expect 0)
3. Search stdout for emoji characters (expect > 0)

**Expected Result (sub-case A):**
- ANSI sequence count: 0
- Emoji characters present: yes (at least one of: any codepoint > 127 that is emoji)
- This proves color and emoji are independent toggles

**Setup (sub-case B: color on, emoji off):**
1. Write config: `{"display": {"use_color": true, "use_emoji": false}}`
2. Remove `NO_COLOR` from env

**Steps (sub-case B):**
1. Invoke statusline.py via subprocess
2. Search stdout for ANSI escape sequences (expect > 0)
3. Search stdout for non-ASCII characters (expect 0)

**Expected Result (sub-case B):**
- ANSI sequence count: > 0
- Non-ASCII (emoji) characters: 0
- This proves the reverse independence

**Cleanup:**
- Remove config file in `finally` block

---

#### VT-EN005-007: Atomic State File Writes

| Attribute | Value |
|-----------|-------|
| **Test ID** | VT-EN005-007 |
| **Requirement(s)** | REQ-EN005-007 |
| **Risk Mitigation** | RSK-EN005-003 (YELLOW 12), RSK-EN005-004 (GREEN 2) |
| **Priority** | 1 (YELLOW risk -- highest score in register) |
| **Test Function** | `run_atomic_write_test()` (to be added in GREEN phase -- TASK-005) |
| **Source File** | `test_statusline.py` (new function, GREEN phase) |
| **Status** | PLANNED (not yet written) |

**Setup:**
1. Create a temporary directory for state file
2. Pre-populate a valid state file with known JSON content
3. Configure statusline to use this state file path via config

**Steps:**
1. Invoke statusline.py with a payload that triggers state write (e.g., compaction payload)
2. After invocation, read the state file and validate it is valid JSON
3. Check the state file directory for orphan temp files (`.tmp` suffix)
4. Verify exit code is 0

**Expected Result:**
- State file contains valid JSON after write
- No orphan `.tmp` files in state directory
- Exit code: 0
- stdout is non-empty

**Implementation Note:** True atomicity (crash-safety) cannot be fully validated in user-space unit tests (per RSK-EN005-006). This test validates functional correctness and temp file cleanup. Atomicity is confirmed by code inspection of the `save_state()` implementation (verifying temp-write + os.replace pattern).

**Cleanup:**
- Remove temporary directory and all contents

---

#### VT-EN005-008: Atomic Write Graceful Degradation

| Attribute | Value |
|-----------|-------|
| **Test ID** | VT-EN005-008 |
| **Requirement(s)** | REQ-EN005-008 |
| **Risk Mitigation** | RSK-EN005-003 (YELLOW 12) |
| **Priority** | 1 (YELLOW risk mitigation) |
| **Test Function** | `run_readonly_state_test()` (EXISTING -- lines 632-689) |
| **Source File** | `test_statusline.py` lines 632-689 |
| **Status** | PASSING (existing test, serves as regression gate) |

**Setup:**
1. Create a temporary directory
2. Set directory permissions to read-only (`0o444`)
3. Configure statusline to use a state file path inside this read-only directory

**Steps:**
1. Invoke statusline.py via subprocess with the read-only state config
2. Verify exit code is 0
3. Verify stdout is non-empty

**Expected Result:**
- Exit code: 0 (no crash)
- stdout length: > 0 (valid status line produced despite state write failure)
- No temp file orphans (graceful cleanup)

**Cleanup:**
- Restore directory permissions to `0o755`
- Remove temporary directory via `shutil.rmtree()`

---

#### VT-EN005-009: Error Handling Contract Preservation (Regression Suite)

| Attribute | Value |
|-----------|-------|
| **Test ID** | VT-EN005-009 |
| **Requirement(s)** | REQ-EN005-009 |
| **Risk Mitigation** | RSK-EN005-002 (YELLOW 6) |
| **Priority** | 1 (regression gate) |
| **Test Function** | 4 existing tests (composite regression) |
| **Source File** | `test_statusline.py` |
| **Status** | PASSING (all 4 existing tests pass) |

**Component Tests:**

| Sub-Test | Function | Lines | What It Validates |
|----------|----------|-------|-------------------|
| VT-EN005-009a | `run_compaction_test()` | 499-550 | State file read/write cycle with compaction detection |
| VT-EN005-009b | `run_readonly_state_test()` | 632-689 | Graceful degradation on read-only filesystem |
| VT-EN005-009c | `run_no_home_test()` | 553-592 | State path resolution when HOME is unset |
| VT-EN005-009d | `run_corrupt_state_test()` | 744-801 | State file parsing with invalid JSON |

**Pass Criteria:**
- All 4 component tests pass with exit code 0 after EN-005 code changes
- No modifications to these test functions are permitted (regression-only)

---

#### VT-EN005-010: Git Timeout Configuration

| Attribute | Value |
|-----------|-------|
| **Test ID** | VT-EN005-010 |
| **Requirement(s)** | REQ-EN005-010 |
| **Risk Mitigation** | N/A (GREEN risk, existing functionality) |
| **Priority** | 2 (GREEN risk -- formalizes existing behavior) |
| **Test Function** | `run_git_timeout_config_test()` (to be added in GREEN phase -- TASK-003) |
| **Source File** | `test_statusline.py` (new function, GREEN phase) |
| **Status** | PLANNED (not yet written) |

**Setup:**
1. Write config file with `{"advanced": {"git_timeout": 10}}`
2. Set `ECW_DEBUG=1` in environment to enable debug logging

**Steps:**
1. Invoke statusline.py via subprocess with the config and debug env
2. Search stderr for debug log message containing `git_timeout` or `timeout` with value `10`
3. Verify exit code is 0

**Expected Result:**
- Exit code: 0
- Debug output references configured timeout value (10)
- stdout is non-empty (status line rendered)

**Alternative Verification:** If debug logging does not expose the timeout value, verify by code inspection that `get_git_info()` reads `config["advanced"]["git_timeout"]` and passes it to `subprocess.run(timeout=...)`.

**Cleanup:**
- Remove config file in `finally` block

---

### Inspection Procedures

---

#### VI-EN005-001: use_color Default in DEFAULT_CONFIG

| Attribute | Value |
|-----------|-------|
| **Inspection ID** | VI-EN005-001 |
| **Requirement(s)** | REQ-EN005-004 |
| **Risk Mitigation** | RSK-EN005-009 (GREEN 4) |
| **Priority** | 2 (code-structural check) |
| **Document** | `statusline.py` |
| **Status** | PLANNED |

**Checklist:**

- [ ] `DEFAULT_CONFIG` dictionary contains a `"display"` section
- [ ] `DEFAULT_CONFIG["display"]` contains key `"use_color"` with value `True`
- [ ] `"use_color"` is positioned alongside `"use_emoji"` in the `"display"` section
- [ ] The default value `True` preserves existing behavior (no change for users who do not set it)
- [ ] `deep_merge()` / config loading correctly merges partial user configs (a user config with `{"display": {"compact_mode": true}}` does not remove `use_color` default)

---

#### VI-EN005-002: git_timeout Documentation in GETTING_STARTED.md

| Attribute | Value |
|-----------|-------|
| **Inspection ID** | VI-EN005-002 |
| **Requirement(s)** | REQ-EN005-011 |
| **Risk Mitigation** | N/A |
| **Priority** | 3 (documentation) |
| **Document** | `GETTING_STARTED.md` |
| **Status** | PLANNED |

**Checklist:**

- [ ] Configuration options table includes `advanced.git_timeout`
- [ ] Default value is documented as `2` (seconds)
- [ ] Description explains purpose: "Git command timeout in seconds"
- [ ] Usage example provided for large monorepos (e.g., `"git_timeout": 10`)
- [ ] Cross-reference to Troubleshooting section for "git segment not showing"
- [ ] Valid range or type constraint documented (numeric, positive)

---

#### VI-EN005-003: UNC Path Limitations Documentation

| Attribute | Value |
|-----------|-------|
| **Inspection ID** | VI-EN005-003 |
| **Requirement(s)** | REQ-EN005-012 |
| **Risk Mitigation** | RSK-EN005-007 (YELLOW 6) |
| **Priority** | 3 (documentation with YELLOW risk) |
| **Document** | `GETTING_STARTED.md` |
| **Status** | PLANNED |

**Checklist:**

- [ ] Dedicated section/subsection for UNC paths exists (titled "UNC Paths" or "Network Drives" or equivalent)
- [ ] Documents `Path.home()` behavior on UNC paths (may return None or raise)
- [ ] Documents state file write limitations on network paths (latency, locking)
- [ ] Documents git operation considerations (timeout may be exceeded)
- [ ] Documents performance considerations for network-mounted repos
- [ ] Uses conservative hedging language per RSK-EN005-007 mitigation (e.g., "may not work" rather than "does not work")
- [ ] No unverified definitive claims about untested scenarios

---

#### VI-EN005-004: UNC Path Alternatives Documentation

| Attribute | Value |
|-----------|-------|
| **Inspection ID** | VI-EN005-004 |
| **Requirement(s)** | REQ-EN005-013 |
| **Risk Mitigation** | RSK-EN005-007 (YELLOW 6) |
| **Priority** | 3 (documentation) |
| **Document** | `GETTING_STARTED.md` |
| **Status** | PLANNED |

**Checklist:**

- [ ] Alternative 1 documented: Map network drive to drive letter (e.g., `net use Z: \\server\share`)
- [ ] Alternative 2 documented: Use WSL 2 for development on Windows
- [ ] Alternative 3 documented: Clone repository locally instead of working on network share
- [ ] Each alternative includes brief, actionable instructions
- [ ] References `advanced.git_timeout` for users who must work on network paths
- [ ] Positioned within or adjacent to the UNC limitations section

---

#### VI-EN005-005: SSH Terminal Requirements Documentation

| Attribute | Value |
|-----------|-------|
| **Inspection ID** | VI-EN005-005 |
| **Requirement(s)** | REQ-EN005-014 |
| **Risk Mitigation** | RSK-EN005-008 (YELLOW 6) |
| **Priority** | 3 (documentation with YELLOW risk) |
| **Document** | `GETTING_STARTED.md` |
| **Status** | PLANNED |

**Checklist:**

- [ ] Dedicated section for SSH/remote terminals exists
- [ ] TERM variable requirements documented (`xterm-256color` or equivalent)
- [ ] Locale/encoding requirements documented (`LANG=en_US.UTF-8` or similar)
- [ ] Emoji rendering over SSH explained (depends on local terminal emulator, not remote)
- [ ] `NO_COLOR` usage recommended for SSH sessions with poor ANSI support
- [ ] Quick-check command provided: `echo $TERM && echo $LANG`
- [ ] SSH config snippet provided for `SetEnv TERM=xterm-256color`
- [ ] Uses advisory language per RSK-EN005-008 mitigation

---

#### VI-EN005-006: tmux Configuration Documentation

| Attribute | Value |
|-----------|-------|
| **Inspection ID** | VI-EN005-006 |
| **Requirement(s)** | REQ-EN005-015 |
| **Risk Mitigation** | RSK-EN005-008 (YELLOW 6) |
| **Priority** | 3 (documentation) |
| **Document** | `GETTING_STARTED.md` |
| **Status** | PLANNED |

**Checklist:**

- [ ] tmux-specific section exists (standalone or subsection of SSH section)
- [ ] Required `tmux.conf` settings provided:
  - [ ] `set -g default-terminal "tmux-256color"`
  - [ ] `set -ga terminal-overrides ",xterm-256color:Tc"`
- [ ] `default-terminal` recommendation explained (why "screen" is insufficient)
- [ ] Progress bar character rendering considerations noted
- [ ] Note about `use_emoji: false` for older tmux versions (< 3.0)
- [ ] Verification command provided: `tmux display -p '#{client_termname}'`

---

## L1: Risk-Based Test Priority

Tests are ordered by the severity of the risk they mitigate. YELLOW risks (score 6-12) are prioritized first, then GREEN risks, then inspections.

### Priority Tier 1: YELLOW Risk Mitigations (Execute First)

| Priority | Test ID | Requirement(s) | Risk Mitigated | Risk Score | Test Function |
|----------|---------|----------------|----------------|------------|---------------|
| 1.1 | VT-EN005-007 | REQ-EN005-007 | RSK-EN005-003 (os.replace cross-platform) | **12 YELLOW** | `run_atomic_write_test()` (GREEN phase) |
| 1.2 | VT-EN005-008 | REQ-EN005-008 | RSK-EN005-003 (os.replace cross-platform) | **12 YELLOW** | `run_readonly_state_test()` (existing) |
| 1.3 | VT-EN005-001 | REQ-EN005-001, REQ-EN005-003 | RSK-EN005-001 (NO_COLOR interaction) | **9 YELLOW** | `run_no_color_env_test()` |
| 1.4 | VT-EN005-002 | REQ-EN005-002 | RSK-EN005-001 (NO_COLOR interaction) | **9 YELLOW** | `run_color_matrix_test()` scenario 2 |
| 1.5 | VT-EN005-003 | REQ-EN005-003 | RSK-EN005-010 (NO_COLOR edge cases) | **6 YELLOW** | `run_color_matrix_test()` + empty-string cases |
| 1.6 | VT-EN005-005 | REQ-EN005-005 | RSK-EN005-002 (ansi_color regression) | **6 YELLOW** | `run_use_color_disabled_test()` |
| 1.7 | VT-EN005-006 | REQ-EN005-006 | RSK-EN005-001 (NO_COLOR interaction) | **9 YELLOW** | `run_color_matrix_test()` + independence |
| 1.8 | VT-EN005-009 | REQ-EN005-009 | RSK-EN005-002 (ansi_color regression), RSK-EN005-005 (test interference) | **8 YELLOW** | Existing regression suite (4 tests) |

### Priority Tier 2: GREEN Risk Mitigations

| Priority | Test ID | Requirement(s) | Risk Mitigated | Risk Score | Test Function |
|----------|---------|----------------|----------------|------------|---------------|
| 2.1 | VT-EN005-004 | REQ-EN005-004 | RSK-EN005-009 (config backward compat) | **4 GREEN** | `run_color_matrix_test()` scenario 1 |
| 2.2 | VT-EN005-010 | REQ-EN005-010 | N/A (existing behavior) | **N/A** | `run_git_timeout_config_test()` (GREEN phase) |

### Priority Tier 3: Inspections (Execute Last)

| Priority | Inspection ID | Requirement(s) | Risk Mitigated | Risk Score | Document |
|----------|---------------|----------------|----------------|------------|----------|
| 3.1 | VI-EN005-003 | REQ-EN005-012 | RSK-EN005-007 (UNC doc accuracy) | **6 YELLOW** | `GETTING_STARTED.md` |
| 3.2 | VI-EN005-004 | REQ-EN005-013 | RSK-EN005-007 (UNC doc accuracy) | **6 YELLOW** | `GETTING_STARTED.md` |
| 3.3 | VI-EN005-005 | REQ-EN005-014 | RSK-EN005-008 (SSH/tmux accuracy) | **6 YELLOW** | `GETTING_STARTED.md` |
| 3.4 | VI-EN005-006 | REQ-EN005-015 | RSK-EN005-008 (SSH/tmux accuracy) | **6 YELLOW** | `GETTING_STARTED.md` |
| 3.5 | VI-EN005-001 | REQ-EN005-004 | RSK-EN005-009 (config compat) | **4 GREEN** | `statusline.py` |
| 3.6 | VI-EN005-002 | REQ-EN005-011 | N/A | **N/A** | `GETTING_STARTED.md` |

---

## L2: Traceability

### Forward Traceability: Requirements to Verification Activities

| Requirement | Verification Activity | Type | Status |
|-------------|----------------------|------|--------|
| REQ-EN005-001 | VT-EN005-001 | Test | PLANNED |
| REQ-EN005-002 | VT-EN005-002 | Test | PLANNED |
| REQ-EN005-003 | VT-EN005-003 | Test | PLANNED |
| REQ-EN005-004 | VI-EN005-001 + VT-EN005-004 | Inspection + Test | PLANNED |
| REQ-EN005-005 | VT-EN005-005 | Test | PLANNED |
| REQ-EN005-006 | VT-EN005-006 | Test | PLANNED |
| REQ-EN005-007 | VT-EN005-007 | Test | PLANNED |
| REQ-EN005-008 | VT-EN005-008 | Test | PASSING (existing) |
| REQ-EN005-009 | VT-EN005-009 | Test (regression) | PASSING (existing) |
| REQ-EN005-010 | VT-EN005-010 | Test | PLANNED |
| REQ-EN005-011 | VI-EN005-002 | Inspection | PLANNED |
| REQ-EN005-012 | VI-EN005-003 | Inspection | PLANNED |
| REQ-EN005-013 | VI-EN005-004 | Inspection | PLANNED |
| REQ-EN005-014 | VI-EN005-005 | Inspection | PLANNED |
| REQ-EN005-015 | VI-EN005-006 | Inspection | PLANNED |

**Forward traceability completeness: 15/15 (100%)** -- Every requirement maps to at least one verification activity.

### Backward Traceability: Verification Activities to Requirements

| Verification Activity | Requirement(s) | Type |
|----------------------|----------------|------|
| VT-EN005-001 | REQ-EN005-001, REQ-EN005-003 | Test |
| VT-EN005-002 | REQ-EN005-002 | Test |
| VT-EN005-003 | REQ-EN005-003 | Test |
| VT-EN005-004 | REQ-EN005-004 | Test |
| VT-EN005-005 | REQ-EN005-005 | Test |
| VT-EN005-006 | REQ-EN005-006 | Test |
| VT-EN005-007 | REQ-EN005-007 | Test |
| VT-EN005-008 | REQ-EN005-008 | Test |
| VT-EN005-009 | REQ-EN005-009 | Test (regression) |
| VT-EN005-010 | REQ-EN005-010 | Test |
| VI-EN005-001 | REQ-EN005-004 | Inspection |
| VI-EN005-002 | REQ-EN005-011 | Inspection |
| VI-EN005-003 | REQ-EN005-012 | Inspection |
| VI-EN005-004 | REQ-EN005-013 | Inspection |
| VI-EN005-005 | REQ-EN005-014 | Inspection |
| VI-EN005-006 | REQ-EN005-015 | Inspection |

**Backward traceability completeness: 16/16 (100%)** -- Every verification activity maps to at least one requirement. No orphan tests.

### Coverage Analysis

#### Untested Requirements

None. All 15 requirements have at least one verification activity assigned.

#### Verification Method Distribution

| Method | Count | Requirements |
|--------|-------|-------------|
| Test (automated) | 10 | REQ-EN005-001 through -010 |
| Inspection (manual) | 6 | REQ-EN005-004, -011 through -015 |
| Demonstration | 0 | N/A |
| Analysis | 0 | N/A |

#### Dual-Verified Requirements

| Requirement | Methods | Rationale |
|-------------|---------|-----------|
| REQ-EN005-004 | Test + Inspection | Config key existence is structural (inspection) but behavior is functional (test) |

#### Risk-to-Verification Coverage

| Risk ID | Risk Score | Mitigating Verification | Coverage |
|---------|------------|------------------------|----------|
| RSK-EN005-001 (YELLOW 9) | 9 | VT-EN005-001, VT-EN005-002, VT-EN005-006 | FULL |
| RSK-EN005-002 (YELLOW 6) | 6 | VT-EN005-005, VT-EN005-009 | FULL |
| RSK-EN005-003 (YELLOW 12) | 12 | VT-EN005-007, VT-EN005-008 | FULL |
| RSK-EN005-004 (GREEN 2) | 2 | VT-EN005-007 (dir= param validates same-FS) | FULL |
| RSK-EN005-005 (YELLOW 8) | 8 | VT-EN005-009 (regression suite validates no interference) | FULL |
| RSK-EN005-006 (GREEN 3) | 3 | VT-EN005-007 (functional) + code inspection (atomicity) | PARTIAL (atomicity by inspection only) |
| RSK-EN005-007 (YELLOW 6) | 6 | VI-EN005-003, VI-EN005-004 (doc review with hedging checklist) | FULL |
| RSK-EN005-008 (YELLOW 6) | 6 | VI-EN005-005, VI-EN005-006 (doc review with advisory checklist) | FULL |
| RSK-EN005-009 (GREEN 4) | 4 | VT-EN005-004, VI-EN005-001 | FULL |
| RSK-EN005-010 (YELLOW 6) | 6 | VT-EN005-003 (empty-string test case) | FULL |

**Risk coverage: 10/10 risks have assigned verification activities (100%)**

### V&V Schedule Alignment with Orchestration Phases

| Orchestration Phase | Verification Activities | Dependencies |
|---------------------|------------------------|--------------|
| **Phase 1 -- RED** (completed) | Tests VT-EN005-001 through VT-EN005-006 written and confirmed RED (failing). VT-EN005-008, VT-EN005-009 confirmed PASSING (existing baseline). | N/A |
| **Phase 2 -- GREEN** (Batch A: Color/ANSI) | Execute VT-EN005-001, VT-EN005-002, VT-EN005-003, VT-EN005-004, VT-EN005-005, VT-EN005-006. Confirm transition from RED to GREEN (all passing). Execute VT-EN005-009 regression. | Implementation of TASK-001 + TASK-006 |
| **Phase 2 -- GREEN** (Batch B: Atomic Writes) | Write and execute VT-EN005-007. Execute VT-EN005-008 and VT-EN005-009 regression. | Implementation of TASK-005 |
| **Phase 2 -- GREEN** (Batch C: Documentation) | Execute VI-EN005-002, VI-EN005-003, VI-EN005-004, VI-EN005-005, VI-EN005-006. Write and execute VT-EN005-010. Execute VI-EN005-001 code inspection. | Implementation of TASK-002, TASK-003, TASK-004 |
| **Phase 3 -- REFACTOR** | Re-execute all VT- tests as regression gate. No new tests expected. | Completion of GREEN phase |
| **Final V&V Gate** | All 10 VT- tests PASSING + all 6 VI- inspections PASSED. Full test suite (`uv run python test_statusline.py`) returns exit code 0. | All phases complete |

### Monitoring Indicators (from Risk Assessment)

The following indicators from NSE-RISK-EN005-001 are incorporated as V&V monitoring gates:

| Indicator | Threshold | Verification Activity | Phase |
|-----------|-----------|----------------------|-------|
| RED phase test count | >= 3 new tests (NO_COLOR, use_color, matrix) | VT-EN005-001, -005, -002/-003/-004/-006 | Phase 1 (completed) |
| GREEN phase regression count | 0 existing test failures | VT-EN005-009 (4 component tests) | Phase 2 (continuous) |
| Full suite pass rate | 100% (all 20+ tests) | All VT- tests | Phase 2/3 |
| NO_COLOR empty string | `NO_COLOR=""` disables colors | VT-EN005-003 | Phase 2 (GREEN) |
| Temp file cleanup | 0 orphan `.tmp` files | VT-EN005-007 | Phase 2 (Batch B) |
| os.replace fallback | Read-only FS produces output | VT-EN005-008 | Phase 2 (Batch B) |
| Adversarial critique score | >= 0.92 weighted rubric | VI-EN005-003 through VI-EN005-006 | Phase 3 |

---

## Appendix A: Test Infrastructure Notes

### Subprocess Isolation Model

All automated tests in `test_statusline.py` use Python's `subprocess.run()` to invoke `statusline.py` in an isolated child process. This provides:

1. **Environment isolation:** Each test constructs its own `env` dictionary via `os.environ.copy()` with explicit additions/removals. The parent process environment is never modified.
2. **Config isolation:** Config files are written to `SCRIPT_DIR / "ecw-statusline-config.json"` and cleaned up in `finally` blocks.
3. **State isolation:** State files use `tempfile.NamedTemporaryFile` with explicit cleanup.
4. **Import isolation:** Each subprocess performs a fresh import of `statusline.py`, eliminating any module-level caching concerns (relevant for NO_COLOR detection at import time vs. runtime).

### ANSI Detection Regex

All color-related tests use the same ANSI detection regex:

```python
ansi_re = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")
```

This matches:
- `\x1b[` -- ESC + `[` (CSI sequence introducer)
- `[0-9;]*` -- zero or more digits and semicolons (parameters)
- `[a-zA-Z]` -- final byte (command character)

This covers `\033[0m` (reset), `\033[38;5;NNNm` (256-color foreground), and all other SGR sequences used by `statusline.py`.

### Test Execution Command

Per project CLAUDE.md rules, all tests must be executed via:

```bash
uv run python test_statusline.py
```

Never use `python3 test_statusline.py` or `python test_statusline.py` directly.

---

## Appendix B: Verification Activity Index

| ID | Type | Requirement(s) | Function/Procedure | Source |
|----|------|----------------|-------------------|--------|
| VT-EN005-001 | Test | REQ-001, REQ-003 | `run_no_color_env_test()` | test_statusline.py:804 |
| VT-EN005-002 | Test | REQ-002 | `run_color_matrix_test()` s2 | test_statusline.py:922 |
| VT-EN005-003 | Test | REQ-003 | `run_color_matrix_test()` s2,s4 + empty | test_statusline.py:922 |
| VT-EN005-004 | Test | REQ-004 | `run_color_matrix_test()` s1 | test_statusline.py:922 |
| VT-EN005-005 | Test | REQ-005 | `run_use_color_disabled_test()` | test_statusline.py:858 |
| VT-EN005-006 | Test | REQ-006 | `run_color_matrix_test()` + independence | test_statusline.py:922 |
| VT-EN005-007 | Test | REQ-007 | `run_atomic_write_test()` | test_statusline.py (GREEN) |
| VT-EN005-008 | Test | REQ-008 | `run_readonly_state_test()` | test_statusline.py:632 |
| VT-EN005-009 | Test | REQ-009 | Regression suite (4 tests) | test_statusline.py |
| VT-EN005-010 | Test | REQ-010 | `run_git_timeout_config_test()` | test_statusline.py (GREEN) |
| VI-EN005-001 | Inspection | REQ-004 | DEFAULT_CONFIG code review | statusline.py |
| VI-EN005-002 | Inspection | REQ-011 | git_timeout doc review | GETTING_STARTED.md |
| VI-EN005-003 | Inspection | REQ-012 | UNC limitations doc review | GETTING_STARTED.md |
| VI-EN005-004 | Inspection | REQ-013 | UNC alternatives doc review | GETTING_STARTED.md |
| VI-EN005-005 | Inspection | REQ-014 | SSH requirements doc review | GETTING_STARTED.md |
| VI-EN005-006 | Inspection | REQ-015 | tmux config doc review | GETTING_STARTED.md |

---

*VCRM generated by nse-verification agent v1.0.0*
*Based on NPR 7123.1D Process 7 -- Verification and Validation*
*Date: 2026-02-12*
