DISCLAIMER: This guidance is AI-generated based on NASA Systems Engineering
standards. It is advisory only and does not constitute official NASA guidance.
All SE decisions require human review and professional engineering judgment.

---

# EN-005 Edge Case Handling: Requirements Specification

**Document ID:** NSE-REQ-EN005-001
**Version:** 1.0
**Date:** 2026-02-11
**Author:** NSE Requirements Agent (AI-generated)
**Process Reference:** NPR 7123.1D Process 2 — Technical Requirements Definition
**Workflow:** en005-20260211-001
**Status:** DRAFT — Requires human review

---

## L0: Executive Summary

### Scope

This requirements specification defines **15 formal requirements** for EN-005 (Edge Case Handling), covering six tasks across three categories:

| Category | Tasks | Requirements | Effort |
|----------|-------|-------------|--------|
| **Functional (Code)** | TASK-001, TASK-005, TASK-006 | REQ-EN005-001 through REQ-EN005-009 | 4h |
| **Configuration** | TASK-003 | REQ-EN005-010, REQ-EN005-011 | 1h |
| **Documentation** | TASK-002, TASK-004 | REQ-EN005-012 through REQ-EN005-015 | 3h |

### Risk Mitigation

These requirements directly mitigate four identified risks from the XPLAT-001 risk register:

| Risk | Score | Mitigation Requirements |
|------|-------|------------------------|
| RSK-XPLAT-008: ANSI Color Support Varies | 12 (YELLOW) | REQ-EN005-001 through REQ-EN005-006 |
| RSK-XPLAT-012: NO_COLOR Standard Not Respected | 10 (YELLOW) | REQ-EN005-001 through REQ-EN005-003 |
| RSK-XPLAT-022: State File Corruption | 8 (YELLOW) | REQ-EN005-007 through REQ-EN005-009 |
| RSK-XPLAT-025: Large Monorepo Git Timeout | 6 (YELLOW) | REQ-EN005-010, REQ-EN005-011 |

### Implementation Impact

All changes affect two files:
- **`statusline.py`** — Functional requirements (9 requirements)
- **`GETTING_STARTED.md`** — Documentation requirements (4 requirements) and configuration documentation (2 requirements)

The implementation maintains the project's core constraint: **single-file, stdlib-only Python 3.9+ deployment** with zero external dependencies.

---

## L1: Requirements Specification

### 1. NO_COLOR Environment Variable Support (TASK-001)

Source: Gap G-016 — NO_COLOR environment variable not respected
Risk: RSK-XPLAT-012 (Score 10, YELLOW)

---

### REQ-EN005-001: NO_COLOR Disables All ANSI Output

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-EN005-001 |
| **Type** | Functional |
| **Priority** | Must |
| **Source** | G-016, RSK-XPLAT-012 |
| **Parent** | EN-005 AC-001 |

**Shall Statement:**
The system SHALL disable all ANSI escape code output when the `NO_COLOR` environment variable is present in the process environment.

**Rationale:**
The NO_COLOR standard (https://no-color.org/) is a widely adopted convention that allows users and automation tools to suppress colored output. The current `ansi_color()` function (statusline.py lines 302-306) and `ansi_reset()` function (lines 309-311) unconditionally emit ANSI escape sequences. Terminal multiplexers, CI/CD pipelines, accessibility tools, and log aggregators may not handle ANSI codes correctly, producing garbled output.

**Implementation Guidance:**
- Modify `ansi_color(code: int) -> str` to return empty string `""` when NO_COLOR is detected.
- Modify `ansi_reset() -> str` to return empty string `""` when NO_COLOR is detected.
- Detection should be checked once at startup (or lazily cached) to avoid per-call `os.environ` lookups.

**Verification Method:** Test
**Verification Reference:** New test: `run_no_color_test()` — invoke `statusline.py` with `NO_COLOR=1` in environment, assert output contains zero ANSI escape sequences (no `\033[` substrings).

---

### REQ-EN005-002: NO_COLOR Precedence Over Config

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-EN005-002 |
| **Type** | Functional |
| **Priority** | Must |
| **Source** | G-016, RSK-XPLAT-012 |
| **Parent** | EN-005 AC-001 |

**Shall Statement:**
The system SHALL treat the `NO_COLOR` environment variable as having higher precedence than the `use_color` configuration option, such that when `NO_COLOR` is present, ANSI output is disabled regardless of the `use_color` setting.

**Rationale:**
Environment variables represent the user's or system's runtime intent and should override static file-based configuration. The NO_COLOR standard explicitly states that "when set, [NO_COLOR] should override any configuration that enables color." If `use_color: true` is set in `ecw-statusline-config.json` but the environment has `NO_COLOR`, the environment variable must win. This follows the principle of least surprise and ensures automation pipelines can reliably disable color without modifying config files.

**Implementation Guidance:**
- The color resolution order should be: (1) check `NO_COLOR` environment variable, (2) if not present, check `use_color` config option, (3) if neither, default to colors enabled.

**Verification Method:** Test
**Verification Reference:** New test: `run_no_color_overrides_config_test()` — invoke with both `NO_COLOR=1` environment variable AND `{"display": {"use_color": true}}` config. Assert output contains zero ANSI escape sequences.

---

### REQ-EN005-003: NO_COLOR Standard Compliance

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-EN005-003 |
| **Type** | Functional |
| **Priority** | Must |
| **Source** | G-016, RSK-XPLAT-012 |
| **Parent** | EN-005 AC-001 |

**Shall Statement:**
The system SHALL check for the presence of the `NO_COLOR` environment variable (i.e., the key exists in `os.environ`), not its value, to determine whether to disable color output, in compliance with the no-color.org specification.

**Rationale:**
The no-color.org standard specifies: "Command-line software which outputs text with ANSI color added should check for the presence of a NO_COLOR environment variable that, when present (regardless of its value, including empty), prevents ANSI color." This means `NO_COLOR=""` (empty string), `NO_COLOR=0`, and `NO_COLOR=1` must all disable color. Checking the value (e.g., treating `NO_COLOR=0` as "colors enabled") would violate the standard.

**Implementation Guidance:**
- Use `"NO_COLOR" in os.environ` rather than `os.environ.get("NO_COLOR") == "1"` or truthiness checks.
- This is a common implementation mistake; the check must be presence-based, not value-based.

**Verification Method:** Test
**Verification Reference:** New tests: (a) `NO_COLOR=""` disables color, (b) `NO_COLOR=0` disables color, (c) `NO_COLOR=1` disables color, (d) `NO_COLOR` absent enables color (with default config).

---

### 2. ANSI Color Toggle Configuration (TASK-006)

Source: Gap G-021 — ANSI color toggle config option
Risk: RSK-XPLAT-008 (Score 12, YELLOW)

---

### REQ-EN005-004: use_color Config Toggle with Default True

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-EN005-004 |
| **Type** | Functional |
| **Priority** | Must |
| **Source** | G-021, RSK-XPLAT-008 |
| **Parent** | EN-005 AC-001 (implicit — ANSI control) |

**Shall Statement:**
The system SHALL provide a `display.use_color` configuration option in `DEFAULT_CONFIG` with a default value of `true`.

**Rationale:**
The current `DEFAULT_CONFIG` (statusline.py lines 61-84) includes `use_emoji: True` under the `display` section but has no equivalent toggle for ANSI color codes. Users on terminals with poor ANSI support (e.g., legacy Windows cmd.exe, serial consoles, Braille terminals) need a persistent configuration mechanism to disable colors without setting an environment variable on every invocation.

**Implementation Guidance:**
- Add `"use_color": True` to `DEFAULT_CONFIG["display"]` at approximately line 67, alongside `use_emoji`.
- This is a config-schema change only; the behavioral impact is defined in REQ-EN005-005.

**Verification Method:** Inspection
**Verification Reference:** Code review of `DEFAULT_CONFIG` dict — verify `display.use_color` key exists with value `True`.

---

### REQ-EN005-005: use_color=false Disables ANSI Codes

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-EN005-005 |
| **Type** | Functional |
| **Priority** | Must |
| **Source** | G-021, RSK-XPLAT-008 |
| **Parent** | EN-005 AC-001 (implicit — ANSI control) |

**Shall Statement:**
The system SHALL suppress all ANSI escape code output when `display.use_color` is set to `false` in the configuration file, and the `NO_COLOR` environment variable is not present.

**Rationale:**
When `use_color` is `false`, the `ansi_color()` and `ansi_reset()` functions must return empty strings, producing plain-text output. This provides a persistent, file-based mechanism for users who always want uncolored output without relying on environment variables. The condition "NO_COLOR is not present" is specified for completeness; per REQ-EN005-002, NO_COLOR always overrides, so this requirement governs the case where NO_COLOR is absent.

**Implementation Guidance:**
- The config must be accessible to `ansi_color()` and `ansi_reset()`. Options: (a) pass config as parameter, (b) use a module-level flag set during `load_config()`, or (c) use a closure/global. Option (b) is recommended for minimal API disruption.
- When `use_color` is `false`, `ansi_color()` returns `""` and `ansi_reset()` returns `""`.

**Verification Method:** Test
**Verification Reference:** New test: `run_use_color_disabled_test()` — invoke with config `{"display": {"use_color": false}}`, assert output contains zero ANSI escape sequences.

---

### REQ-EN005-006: use_color Independent of use_emoji

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-EN005-006 |
| **Type** | Functional |
| **Priority** | Must |
| **Source** | G-021, RSK-XPLAT-008 |
| **Parent** | EN-005 AC-001 (implicit — ANSI control) |

**Shall Statement:**
The system SHALL treat the `display.use_color` and `display.use_emoji` configuration options as independent toggles, such that disabling one does not affect the other.

**Rationale:**
A user may want emoji icons without ANSI colors (e.g., a terminal that renders Unicode but not escape sequences), or ANSI colors without emoji (e.g., a terminal with color support but a font lacking emoji glyphs). These are orthogonal display concerns. The existing `use_emoji` toggle (statusline.py line 67) already controls emoji independently; `use_color` must follow the same pattern.

**Implementation Guidance:**
- The four valid combinations must all be supported:
  - `use_color: true, use_emoji: true` — Full output (default)
  - `use_color: true, use_emoji: false` — Colors but no emoji
  - `use_color: false, use_emoji: true` — Emoji but no colors
  - `use_color: false, use_emoji: false` — Plain ASCII

**Verification Method:** Test
**Verification Reference:** New test: `run_color_emoji_independence_test()` — invoke with `{"display": {"use_color": false, "use_emoji": true}}`, assert output has emoji characters but no ANSI escape sequences.

---

### 3. Atomic State File Writes (TASK-005)

Source: Gap G-026 — Atomic state file writes
Risk: RSK-XPLAT-022 (Score 8, YELLOW)

---

### REQ-EN005-007: Atomic Write Pattern for State Files

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-EN005-007 |
| **Type** | Functional |
| **Priority** | Must |
| **Source** | G-026, RSK-XPLAT-022 |
| **Parent** | EN-005 AC-005 |

**Shall Statement:**
The system SHALL write state files using an atomic write pattern consisting of: (1) write data to a temporary file in the same directory as the target, (2) flush and sync the temporary file, (3) rename the temporary file to the target path.

**Rationale:**
The current `save_state()` function (statusline.py lines 277-294) opens the target file directly with `open(state_file, "w")` and writes JSON. If the process is interrupted during write (e.g., by SIGKILL, power loss, or OS crash), the state file may be left truncated or empty. The atomic write pattern (write-to-temp, then rename) ensures the target file is either the old complete version or the new complete version, never a partial write. The `os.rename()` operation is atomic on POSIX filesystems; on Windows, `os.replace()` provides the same guarantee.

**Implementation Guidance:**
- Use `tempfile.NamedTemporaryFile(dir=state_file.parent, delete=False)` to create the temp file in the same directory (required for atomic rename on the same filesystem).
- Write JSON to temp file, then `f.flush()` and `os.fsync(f.fileno())`.
- Use `os.replace(temp_path, state_file)` (works on both POSIX and Windows, unlike `os.rename()` which fails on Windows if the target exists).
- Clean up the temp file in a `finally` block if rename fails.

**Verification Method:** Test
**Verification Reference:** New test: `run_atomic_write_test()` — verify that `save_state()` creates a temp file and renames it, and that an interrupted write does not corrupt the existing state file.

---

### REQ-EN005-008: Atomic Write Graceful Degradation

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-EN005-008 |
| **Type** | Functional |
| **Priority** | Must |
| **Source** | G-026, RSK-XPLAT-022 |
| **Parent** | EN-005 AC-005 |

**Shall Statement:**
The system SHALL degrade gracefully when atomic write operations fail (e.g., due to read-only filesystem, permission errors, or disk full conditions), by logging a debug message and continuing execution without raising an exception to the caller.

**Rationale:**
The status line is a non-critical display component. A failure to persist state should never prevent the status line from rendering output. The current `save_state()` already catches `OSError` (line 293-294); the atomic write implementation must preserve this behavior and additionally handle failures during temp file creation, sync, and rename.

**Implementation Guidance:**
- Wrap the entire atomic write sequence in a try/except that catches `OSError`.
- In the except handler, attempt to clean up any orphaned temp file, then call `debug_log()`.
- The function must not raise exceptions to callers under any failure scenario.

**Verification Method:** Test
**Verification Reference:** Existing test: `run_readonly_state_test()` must continue to pass. New test: verify temp file cleanup on failure.

---

### REQ-EN005-009: Atomic Write Preserves Error Handling Contract

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-EN005-009 |
| **Type** | Functional |
| **Priority** | Must |
| **Source** | G-026, RSK-XPLAT-022 |
| **Parent** | EN-005 AC-005 |

**Shall Statement:**
The system SHALL preserve the existing error handling contract of the `save_state()` function, specifically: (1) returning `None` in all cases, (2) never raising exceptions, (3) logging failures via `debug_log()`, and (4) handling the case where `_resolve_state_path()` returns `None`.

**Rationale:**
The current `save_state()` function has a well-defined error handling contract (statusline.py lines 277-294) that multiple callers depend on (e.g., `extract_compaction_info()` at line 544). Introducing atomic writes must not change the function's signature, return type, or exception behavior. This is a regression-prevention requirement.

**Implementation Guidance:**
- The function signature `save_state(config: Dict, state: Dict[str, Any]) -> None` must not change.
- The early return when `state_file is None` (line 285-287) must be preserved.
- All existing tests that exercise `save_state()` must continue to pass without modification.

**Verification Method:** Test
**Verification Reference:** All existing tests must pass unchanged. Specifically: `run_compaction_test()`, `run_readonly_state_test()`, `run_no_home_test()`, `run_corrupt_state_test()`.

---

### 4. Configurable Git Timeout (TASK-003)

Source: Gap G-018 — Large monorepo git timeout
Risk: RSK-XPLAT-025 (Score 6, YELLOW)

---

### REQ-EN005-010: git_timeout Configurable via Config File

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-EN005-010 |
| **Type** | Functional |
| **Priority** | Should |
| **Source** | G-018, RSK-XPLAT-025 |
| **Parent** | EN-005 AC-003 |

**Shall Statement:**
The system SHALL support configuration of the git command timeout via the `advanced.git_timeout` key in the configuration file, accepting a numeric value representing seconds.

**Rationale:**
The `advanced.git_timeout` key already exists in `DEFAULT_CONFIG` (statusline.py line 156) with a default value of `2` seconds, and is already consumed by `get_git_info()` (line 603). This requirement formalizes the existing behavior and confirms that the config file override mechanism (via `deep_merge()`) correctly applies user-specified values. For large monorepos (e.g., chromium, linux kernel), git operations may exceed 2 seconds, causing the git segment to silently disappear.

**Implementation Guidance:**
- The implementation already exists. This requirement formalizes the behavior and mandates documentation (see REQ-EN005-011).
- Verify that `deep_merge()` correctly overrides `advanced.git_timeout` from user config.
- The value must be numeric (int or float); non-numeric values should fall back to the default.

**Verification Method:** Test
**Verification Reference:** New test: `run_git_timeout_config_test()` — invoke with config `{"advanced": {"git_timeout": 10}}` and verify the configured value is used (can verify via debug log output with `ECW_DEBUG=1`).

---

### REQ-EN005-011: git_timeout Documented in GETTING_STARTED.md

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-EN005-011 |
| **Type** | Documentation |
| **Priority** | Must |
| **Source** | G-018, RSK-XPLAT-025 |
| **Parent** | EN-005 AC-003 |

**Shall Statement:**
The `GETTING_STARTED.md` documentation SHALL include the `advanced.git_timeout` configuration option in the configuration options table, with its default value (2 seconds), valid range, and a usage example for large monorepos.

**Rationale:**
The `GETTING_STARTED.md` configuration options table (lines 519-528) lists key configuration settings but does not include `advanced.git_timeout`. The Troubleshooting section (line 887-893) mentions increasing the timeout but does not explain it as a first-class configuration option. Users with large repos need to discover this setting proactively, not only after encountering the "git segment not showing" problem.

**Implementation Guidance:**
- Add `advanced.git_timeout` to the Configuration options table with: Default=`2`, Description="Git command timeout in seconds. Increase for large monorepos."
- Add a note in the Troubleshooting > Git segment section referencing the config table.

**Verification Method:** Inspection
**Verification Reference:** Review `GETTING_STARTED.md` for presence of `advanced.git_timeout` documentation with default value, description, and example.

---

### 5. UNC Path Documentation (TASK-002)

Source: Gap G-017 — UNC path handling on Windows
Risk: (No directly associated risk — documentation gap)

---

### REQ-EN005-012: UNC Path Limitations Documented

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-EN005-012 |
| **Type** | Documentation |
| **Priority** | Must |
| **Source** | G-017 |
| **Parent** | EN-005 AC-002 |

**Shall Statement:**
The `GETTING_STARTED.md` documentation SHALL include a section documenting known limitations when the working directory is a UNC path (e.g., `\\server\share\path`), including: (1) `Path.home()` behavior on UNC paths, (2) state file write limitations, (3) git operations on network paths, and (4) performance considerations.

**Rationale:**
UNC paths are common in enterprise Windows environments (network drives, DFS shares). The script uses `Path.home()` (statusline.py line 564), `os.path.expanduser()` (line 253), and `subprocess.run()` with `cwd` parameter (lines 610-616), all of which may behave differently on UNC paths. Without documentation, users on network drives may encounter silent failures in the directory segment, state persistence, or git integration without understanding why.

**Implementation Guidance:**
- Add a new subsection under the Windows section or Troubleshooting section titled "UNC Paths (Network Drives)".
- Document specific behaviors:
  - `Path.home()` returns `None` or raises on some UNC configurations
  - State file writes to UNC paths may have latency or locking issues
  - Git operations on network-mounted repos may exceed the default 2-second timeout
  - Directory abbreviation (`abbreviate_home`) may not work correctly

**Verification Method:** Inspection
**Verification Reference:** Review `GETTING_STARTED.md` for UNC path documentation section with the four listed topics.

---

### REQ-EN005-013: UNC Path Alternative Recommendations

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-EN005-013 |
| **Type** | Documentation |
| **Priority** | Should |
| **Source** | G-017 |
| **Parent** | EN-005 AC-002 |

**Shall Statement:**
The UNC path documentation SHALL include recommended alternatives for users experiencing UNC path issues, specifically: (1) mapping the network drive to a drive letter, (2) using WSL 2 for development on Windows, and (3) cloning repositories locally rather than working directly on network shares.

**Rationale:**
Documenting limitations without providing actionable workarounds leaves users stuck. The three recommended alternatives address the root cause (UNC path semantics) rather than attempting to patch every edge case in the script. Mapped drives (`Z:\project`) behave like local paths from the script's perspective. WSL 2 eliminates UNC path issues entirely. Local clones provide the best performance.

**Implementation Guidance:**
- Include a "Recommended Alternatives" subsection within the UNC path documentation.
- Provide brief, actionable instructions for each alternative.
- Note that `advanced.git_timeout` should be increased if working on network paths.

**Verification Method:** Inspection
**Verification Reference:** Review `GETTING_STARTED.md` UNC path section for three specific alternatives with actionable guidance.

---

### 6. SSH/tmux Terminal Documentation (TASK-004)

Source: Gap G-019 — SSH/tmux terminal documentation
Risk: (No directly associated risk — documentation gap)

---

### REQ-EN005-014: SSH Terminal Requirements Documented

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-EN005-014 |
| **Type** | Documentation |
| **Priority** | Should |
| **Source** | G-019 |
| **Parent** | EN-005 AC-004 |

**Shall Statement:**
The `GETTING_STARTED.md` documentation SHALL include a section documenting SSH terminal requirements and compatibility considerations, including: (1) `TERM` environment variable requirements (must be `xterm-256color` or equivalent), (2) locale/encoding requirements (`LANG=en_US.UTF-8` or similar), (3) emoji rendering over SSH (depends on local terminal, not remote), and (4) `NO_COLOR` usage for SSH sessions with poor ANSI support.

**Rationale:**
SSH sessions inherit the remote server's `TERM` and locale settings, which may differ from the user's local terminal. A user connecting from iTerm2 (full emoji and color support) to a remote server with `TERM=vt100` will see garbled output. Documenting the requirements allows users to configure their SSH sessions correctly or disable features that their session cannot support.

**Implementation Guidance:**
- Add a new section "SSH and Remote Terminals" in `GETTING_STARTED.md`, positioned after the Docker section or in a new "Remote Environments" section.
- Include a quick-check command: `echo $TERM && echo $LANG`
- Include SSH config snippet for setting `TERM`:
  ```
  Host myserver
    SetEnv TERM=xterm-256color
  ```

**Verification Method:** Inspection
**Verification Reference:** Review `GETTING_STARTED.md` for SSH documentation section with the four listed topics and actionable configuration examples.

---

### REQ-EN005-015: tmux Configuration Documented

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-EN005-015 |
| **Type** | Documentation |
| **Priority** | Should |
| **Source** | G-019 |
| **Parent** | EN-005 AC-004 |

**Shall Statement:**
The `GETTING_STARTED.md` documentation SHALL include tmux-specific configuration guidance, including: (1) required `tmux.conf` settings for 256-color and UTF-8 support, (2) tmux `default-terminal` setting recommendation, and (3) known tmux-specific rendering considerations for the progress bar characters.

**Rationale:**
tmux is widely used by developers who run Claude Code in long-lived sessions. tmux interposes its own terminal emulation layer, which can strip ANSI codes or misrender Unicode characters if not configured correctly. The default tmux `TERM` is `screen`, which does not advertise 256-color support. Without proper configuration (`set -g default-terminal "tmux-256color"`), all color output will be stripped, making the status line unreadable.

**Implementation Guidance:**
- Include in the same section as SSH documentation or as a subsection.
- Provide the minimal `~/.tmux.conf` settings:
  ```
  set -g default-terminal "tmux-256color"
  set -ga terminal-overrides ",xterm-256color:Tc"
  ```
- Note that `use_emoji: false` may be needed on older tmux versions (< 3.0) with certain terminal emulators.
- Include a verification command: `tmux display -p '#{client_termname}'`

**Verification Method:** Inspection
**Verification Reference:** Review `GETTING_STARTED.md` for tmux configuration section with `tmux.conf` examples and verification command.

---

## L2: Traceability Matrix

### Requirements to Source Gaps

| Requirement | Gap | Gap Description |
|-------------|-----|-----------------|
| REQ-EN005-001 | G-016 | NO_COLOR environment variable not respected |
| REQ-EN005-002 | G-016 | NO_COLOR environment variable not respected |
| REQ-EN005-003 | G-016 | NO_COLOR environment variable not respected |
| REQ-EN005-004 | G-021 | ANSI color toggle config option |
| REQ-EN005-005 | G-021 | ANSI color toggle config option |
| REQ-EN005-006 | G-021 | ANSI color toggle config option |
| REQ-EN005-007 | G-026 | Atomic state file writes |
| REQ-EN005-008 | G-026 | Atomic state file writes |
| REQ-EN005-009 | G-026 | Atomic state file writes |
| REQ-EN005-010 | G-018 | Large monorepo git timeout |
| REQ-EN005-011 | G-018 | Large monorepo git timeout |
| REQ-EN005-012 | G-017 | UNC path handling on Windows |
| REQ-EN005-013 | G-017 | UNC path handling on Windows |
| REQ-EN005-014 | G-019 | SSH/tmux terminal documentation |
| REQ-EN005-015 | G-019 | SSH/tmux terminal documentation |

### Requirements to Risks

| Requirement | Risk ID | Risk Description | Risk Score |
|-------------|---------|-------------------|------------|
| REQ-EN005-001 | RSK-XPLAT-012 | NO_COLOR Standard Not Respected | 10 (YELLOW) |
| REQ-EN005-002 | RSK-XPLAT-012 | NO_COLOR Standard Not Respected | 10 (YELLOW) |
| REQ-EN005-003 | RSK-XPLAT-012 | NO_COLOR Standard Not Respected | 10 (YELLOW) |
| REQ-EN005-004 | RSK-XPLAT-008 | ANSI Color Support Varies | 12 (YELLOW) |
| REQ-EN005-005 | RSK-XPLAT-008 | ANSI Color Support Varies | 12 (YELLOW) |
| REQ-EN005-006 | RSK-XPLAT-008 | ANSI Color Support Varies | 12 (YELLOW) |
| REQ-EN005-007 | RSK-XPLAT-022 | State File Corruption | 8 (YELLOW) |
| REQ-EN005-008 | RSK-XPLAT-022 | State File Corruption | 8 (YELLOW) |
| REQ-EN005-009 | RSK-XPLAT-022 | State File Corruption | 8 (YELLOW) |
| REQ-EN005-010 | RSK-XPLAT-025 | Large Monorepo Git Timeout | 6 (YELLOW) |
| REQ-EN005-011 | RSK-XPLAT-025 | Large Monorepo Git Timeout | 6 (YELLOW) |
| REQ-EN005-012 | — | No direct risk (documentation gap) | — |
| REQ-EN005-013 | — | No direct risk (documentation gap) | — |
| REQ-EN005-014 | — | No direct risk (documentation gap) | — |
| REQ-EN005-015 | — | No direct risk (documentation gap) | — |

### Requirements to Acceptance Criteria

| Requirement | EN-005 Acceptance Criterion |
|-------------|---------------------------|
| REQ-EN005-001 | AC-001: `NO_COLOR=1` disables all ANSI escape codes |
| REQ-EN005-002 | AC-001: `NO_COLOR=1` disables all ANSI escape codes |
| REQ-EN005-003 | AC-001: `NO_COLOR=1` disables all ANSI escape codes |
| REQ-EN005-004 | (Implicit: ANSI color control capability) |
| REQ-EN005-005 | (Implicit: ANSI color control capability) |
| REQ-EN005-006 | (Implicit: ANSI color control capability) |
| REQ-EN005-007 | AC-005: State file writes use atomic pattern (write temp, rename) |
| REQ-EN005-008 | AC-005: State file writes use atomic pattern (write temp, rename) |
| REQ-EN005-009 | AC-005: State file writes use atomic pattern (write temp, rename) |
| REQ-EN005-010 | AC-003: `git.timeout` configurable in config file |
| REQ-EN005-011 | AC-003: `git.timeout` configurable in config file |
| REQ-EN005-012 | AC-002: UNC paths documented with known limitations |
| REQ-EN005-013 | AC-002: UNC paths documented with known limitations |
| REQ-EN005-014 | AC-004: SSH/tmux terminal compatibility documented |
| REQ-EN005-015 | AC-004: SSH/tmux terminal compatibility documented |

### Requirements to Verification Methods

| Requirement | Type | Method | Reference | Automated? |
|-------------|------|--------|-----------|------------|
| REQ-EN005-001 | Functional | Test | `run_no_color_test()` | Yes |
| REQ-EN005-002 | Functional | Test | `run_no_color_overrides_config_test()` | Yes |
| REQ-EN005-003 | Functional | Test | `run_no_color_empty_value_test()` | Yes |
| REQ-EN005-004 | Functional | Inspection | Code review of `DEFAULT_CONFIG` | No |
| REQ-EN005-005 | Functional | Test | `run_use_color_disabled_test()` | Yes |
| REQ-EN005-006 | Functional | Test | `run_color_emoji_independence_test()` | Yes |
| REQ-EN005-007 | Functional | Test | `run_atomic_write_test()` | Yes |
| REQ-EN005-008 | Functional | Test | `run_readonly_state_test()` (existing) | Yes |
| REQ-EN005-009 | Functional | Test | Existing test suite (regression) | Yes |
| REQ-EN005-010 | Functional | Test | `run_git_timeout_config_test()` | Yes |
| REQ-EN005-011 | Documentation | Inspection | `GETTING_STARTED.md` review | No |
| REQ-EN005-012 | Documentation | Inspection | `GETTING_STARTED.md` review | No |
| REQ-EN005-013 | Documentation | Inspection | `GETTING_STARTED.md` review | No |
| REQ-EN005-014 | Documentation | Inspection | `GETTING_STARTED.md` review | No |
| REQ-EN005-015 | Documentation | Inspection | `GETTING_STARTED.md` review | No |

### Affected Files Matrix

| Requirement | `statusline.py` | `test_statusline.py` | `GETTING_STARTED.md` |
|-------------|:---:|:---:|:---:|
| REQ-EN005-001 | Modify | Add test | — |
| REQ-EN005-002 | Modify | Add test | — |
| REQ-EN005-003 | Modify | Add test | — |
| REQ-EN005-004 | Modify | — | — |
| REQ-EN005-005 | Modify | Add test | — |
| REQ-EN005-006 | — | Add test | — |
| REQ-EN005-007 | Modify | Add test | — |
| REQ-EN005-008 | Modify | Existing test | — |
| REQ-EN005-009 | — | Existing tests | — |
| REQ-EN005-010 | — | Add test | — |
| REQ-EN005-011 | — | — | Add section |
| REQ-EN005-012 | — | — | Add section |
| REQ-EN005-013 | — | — | Add section |
| REQ-EN005-014 | — | — | Add section |
| REQ-EN005-015 | — | — | Add section |

### Implementation Dependency Graph

```
REQ-EN005-004 (add use_color to DEFAULT_CONFIG)
  └── REQ-EN005-005 (use_color=false disables ANSI)
       └── REQ-EN005-002 (NO_COLOR overrides use_color)
            └── REQ-EN005-001 (NO_COLOR disables ANSI)
                 └── REQ-EN005-003 (NO_COLOR presence check)
  └── REQ-EN005-006 (independence from use_emoji)

REQ-EN005-007 (atomic write pattern)
  └── REQ-EN005-008 (graceful degradation)
  └── REQ-EN005-009 (preserve error handling contract)

REQ-EN005-010 (git_timeout configurable) — already implemented, formalized
  └── REQ-EN005-011 (documentation)

REQ-EN005-012 (UNC path documentation) — standalone
  └── REQ-EN005-013 (alternatives) — depends on 012

REQ-EN005-014 (SSH documentation) — standalone
  └── REQ-EN005-015 (tmux documentation) — can be grouped with 014
```

### Recommended Implementation Order

1. **Phase A: Config foundation** — REQ-EN005-004 (add `use_color` to config)
2. **Phase B: Color control** — REQ-EN005-005, REQ-EN005-001, REQ-EN005-003, REQ-EN005-002, REQ-EN005-006
3. **Phase C: Atomic writes** — REQ-EN005-007, REQ-EN005-008, REQ-EN005-009
4. **Phase D: Git timeout** — REQ-EN005-010, REQ-EN005-011
5. **Phase E: Documentation** — REQ-EN005-012, REQ-EN005-013, REQ-EN005-014, REQ-EN005-015

---

## Appendix A: Standards Compliance Notes

### NO_COLOR Standard (no-color.org)

The no-color.org specification states:
> "Command-line software which outputs text with ANSI color added should check for the presence of a NO_COLOR environment variable that, when present (regardless of its value, including empty), prevents ANSI color."

Key compliance points:
- Check **presence**, not **value**: `"NO_COLOR" in os.environ`
- Applies to all ANSI color codes, not just foreground colors
- Does not affect non-color formatting (bold, underline) per strict reading, but common practice disables all escape sequences
- ECW Status Line uses only foreground 256-color codes (`\033[38;5;Nm`), so disabling all ANSI is appropriate

### Atomic Write Pattern (POSIX/Windows)

- POSIX: `os.rename()` is atomic if source and target are on the same filesystem
- Windows: `os.rename()` fails if target exists; `os.replace()` is atomic and works cross-platform (Python 3.3+)
- Both require temp file and target to be on the same filesystem/volume
- `tempfile.NamedTemporaryFile(dir=target_dir)` ensures same-filesystem placement

---

## Appendix B: Code Location References

| Reference | File | Line(s) | Current Behavior |
|-----------|------|---------|-----------------|
| `ansi_color()` | `statusline.py` | 302-306 | Always returns ANSI escape sequence |
| `ansi_reset()` | `statusline.py` | 309-311 | Always returns `\033[0m]` |
| `DEFAULT_CONFIG` | `statusline.py` | 61-159 | Has `use_emoji` but no `use_color` |
| `save_state()` | `statusline.py` | 277-294 | Direct file write, no atomic pattern |
| `advanced.git_timeout` | `statusline.py` | 156 | Default value `2`, consumed at line 603 |
| Config options table | `GETTING_STARTED.md` | 519-528 | Missing `git_timeout` entry |
| Troubleshooting git | `GETTING_STARTED.md` | 886-893 | Mentions timeout increase but no formal docs |

---

*End of Requirements Specification*
