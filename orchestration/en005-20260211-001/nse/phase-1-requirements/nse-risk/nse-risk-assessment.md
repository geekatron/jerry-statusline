# EN-005 Implementation Risk Assessment

> **Document ID:** EN005-NSE-RISK-001
> **Project:** jerry-statusline (ECW Status Line)
> **Workflow ID:** `en005-20260211-001`
> **Work Item:** EN-005 (Edge Case Handling)
> **Author:** nse-risk agent
> **Date:** 2026-02-11
> **Methodology:** NASA NPR 8000.4C 5x5 Risk Matrix
> **Version:** 1.0

---

```
DISCLAIMER: This guidance is AI-generated based on NASA Systems Engineering
standards. It is advisory only and does not constitute official NASA guidance.
All SE decisions require human review and professional engineering judgment.
```

---

## L0: Executive Summary

### Overall Risk Profile

EN-005 implementation carries a **moderate overall risk** profile. The scope is well-bounded (6 tasks, 8 hours, single-file architecture) and the implementation strategy (RED/GREEN/REFACTOR TDD with adversarial critique) provides strong risk mitigation through early defect detection. However, cross-platform behavioral differences (particularly `os.replace()` and `tempfile` on Windows) and the NO_COLOR standard compliance edge cases introduce meaningful risk that requires active management.

**Risk Distribution:**

| Risk Level | Count | Percentage |
|------------|-------|------------|
| RED (15-25) | 0 | 0% |
| YELLOW (6-12) | 4 | 40% |
| GREEN (1-5) | 6 | 60% |
| **Total** | **10** | **100%** |

No RED risks were identified for this implementation scope, which reflects the benefits of a well-bounded, single-file architecture with zero external dependencies. The 4 YELLOW risks require active mitigation during implementation.

### Risk Heat Map (5x5 Matrix)

```
CONSEQUENCE
     |  1-Minimal  2-Marginal  3-Moderate  4-Significant  5-Catastrophic
-----+--------------------------------------------------------------------
  5  |     5          10          15           20             25
Near |   (Green)    (Yellow)     (Red)        (Red)          (Red)
Cert |
     |
-----+--------------------------------------------------------------------
  4  |     4           8          12           16             20
Prob |   (Green)    (Yellow)    (Yellow)      (Red)          (Red)
     |              RSK-005     RSK-003
     |
     |
-----+--------------------------------------------------------------------
  3  |     3           6           9           12             15
Poss |   (Green)    (Yellow)    (Yellow)    (Yellow)         (Red)
     |   RSK-006    RSK-010     RSK-001
     |              RSK-007
     |              RSK-008
-----+--------------------------------------------------------------------
  2  |     2           4           6            8             10
Unlik|   (Green)    (Green)     (Yellow)    (Yellow)       (Yellow)
     |              RSK-009     RSK-002
     |
-----+--------------------------------------------------------------------
  1  |     1           2           3            4              5
Remot|   (Green)    (Green)     (Green)      (Green)        (Green)
     |              RSK-004
-----+--------------------------------------------------------------------
LIKELIHOOD
```

### Top 3 Risks Requiring Attention

| Rank | Risk ID | Title | Score | Rationale |
|------|---------|-------|-------|-----------|
| 1 | RSK-EN005-003 | Atomic write (`os.replace`) cross-platform behavior | **12 (YELLOW)** | Windows file locking semantics differ fundamentally from POSIX; `os.replace()` can fail if another process holds the target file open. Most complex implementation change with highest cross-platform variance. |
| 2 | RSK-EN005-001 | NO_COLOR + use_color interaction complexity | **9 (YELLOW)** | Precedence logic between environment variable and config file creates a 4-scenario interaction matrix. The NO_COLOR standard has a subtle edge case (`NO_COLOR=""` empty string) that is easy to get wrong. |
| 3 | RSK-EN005-005 | New tests interfere with existing test suite | **8 (YELLOW)** | The test suite uses temp config files in the script directory and environment variable manipulation. The 3 new EN-005 tests (NO_COLOR, use_color, color matrix) already exist in the test suite and manipulate shared state (config files, env vars) that could leak. |

---

## L1: Risk Register

### Category 1: Code Modification Risks

---

### RSK-EN005-001: NO_COLOR + use_color Interaction Complexity

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-EN005-001 |
| **Category** | Code Modification |
| **Description** | The precedence logic between `NO_COLOR` environment variable and `use_color` config option creates a 4-scenario interaction matrix. Implementing the correct precedence (NO_COLOR overrides use_color) while handling edge cases (empty string, missing key) introduces logic complexity in `ansi_color()` and `ansi_reset()`. |
| **Root Cause** | Two independent color control mechanisms (env var and config) that must interact correctly, combined with the NO_COLOR standard's specific semantics around empty vs absent values. |
| **Likelihood** | 3 - Possible |
| **Consequence** | 3 - Moderate (incorrect color behavior, standard non-compliance) |
| **Risk Score** | **9 (YELLOW)** |
| **Affected Tasks** | TASK-001, TASK-006 |

**Analysis:**

The `ansi_color()` function (line 302-306) and `ansi_reset()` function (line 309-311) are called from 18 locations throughout `statusline.py` (lines 668, 669, 735, 736, 777, 778, 796, 797, 798, 820, 821, 841, 842, 862, 863, 887, 896, 909, 910, 969, 970). Any behavioral change to these functions has a blast radius of the entire output pipeline. The interaction matrix is:

1. `use_color=true` + `NO_COLOR` unset: Colors PRESENT (default behavior)
2. `use_color=true` + `NO_COLOR` set: Colors ABSENT (NO_COLOR wins)
3. `use_color=false` + `NO_COLOR` unset: Colors ABSENT (config wins)
4. `use_color=false` + `NO_COLOR` set: Colors ABSENT (both agree)

The `no-color.org` standard states: "When set, callers should not add ANSI color escape codes to command output." The standard specifies that the *presence* of the variable matters, not its value. This means `NO_COLOR=""` (empty string) should still disable colors, which is a common implementation error.

**Mitigation Strategy:**
1. Write the 4-scenario color matrix test FIRST (RED phase) before any code changes, as already planned in `test_statusline.py` lines 922-1018
2. Use `os.environ.get("NO_COLOR")` with `is not None` check (not truthiness check) to comply with the standard
3. Evaluate `NO_COLOR` at the point of use in `ansi_color()`/`ansi_reset()` rather than caching at startup, to handle dynamic environment changes
4. Add explicit comment in code citing `https://no-color.org/` for future maintainer reference

**Residual Risk:** 3 (Likelihood 1 x Consequence 3) - GREEN after TDD tests validate all 4 matrix scenarios

---

### RSK-EN005-002: ansi_color() Modification Breaks Existing Tests

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-EN005-002 |
| **Category** | Code Modification |
| **Description** | Modifying `ansi_color()` and `ansi_reset()` could break existing behavior relied upon by the 20 current test assertions (across 17 tests). Existing tests verify ANSI codes are present in output; changing the function signature or default behavior could cause regressions. |
| **Root Cause** | High fan-out of `ansi_color()`/`ansi_reset()` (called from 18+ locations). Any change to return value or behavior propagates to all segments. |
| **Likelihood** | 2 - Unlikely |
| **Consequence** | 3 - Moderate (test failures block CI, rework required) |
| **Risk Score** | **6 (YELLOW)** |
| **Affected Tasks** | TASK-001, TASK-006 |

**Analysis:**

The existing test suite (`test_statusline.py`, 1149 lines, 20 tests) does not explicitly check for ANSI escape sequences in most tests. However, the `run_emoji_disabled_test()` (line 692) checks for non-ASCII characters, and if `ansi_color()` starts returning unexpected values, the character-level assertions could fail in surprising ways.

The key invariant that must be preserved: when NO_COLOR is NOT set and use_color is NOT explicitly false (i.e., default behavior), `ansi_color()` must continue returning `\033[38;5;{code}m` exactly as before. The modification must be additive only (new code path for suppression), not a restructuring of the existing path.

Importantly, tests `run_no_color_env_test()` (line 804), `run_use_color_disabled_test()` (line 858), and `run_color_matrix_test()` (line 922) already exist in the test suite. This means the RED phase tests are already written. This significantly reduces regression risk because the test infrastructure for validating the new behavior already exists and captures the expected contract.

**Mitigation Strategy:**
1. Run the full existing test suite (`uv run python test_statusline.py`) BEFORE making any code changes to establish baseline
2. Structure the `ansi_color()`/`ansi_reset()` modifications as an early-return guard clause at the top of each function (check NO_COLOR/use_color, return "" if disabled)
3. Preserve the existing function signature `ansi_color(code: int) -> str` unchanged; the config must be accessed via module-level or closure, not via parameter change
4. Run full test suite after each atomic change (NO_COLOR first, then use_color)

**Residual Risk:** 2 (Likelihood 1 x Consequence 2) - GREEN after TDD validation confirms no regression

---

### RSK-EN005-003: Atomic Write (os.replace) Cross-Platform Behavior

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-EN005-003 |
| **Category** | Code Modification |
| **Description** | `os.replace()` is specified as atomic on POSIX systems but has different semantics on Windows. On Windows, `os.replace()` can fail with `PermissionError` if the target file is open by another process (file locking). Additionally, `tempfile.NamedTemporaryFile` on Windows defaults to `delete=True` with file locking that prevents `os.replace()` from working while the file is still open. |
| **Root Cause** | Windows NTFS file locking model differs from POSIX. On POSIX, `os.replace()` is a rename(2) syscall that atomically replaces the target. On Windows, the target file must not be open by any process for `os.replace()` to succeed. `NamedTemporaryFile` on Windows uses `O_TEMPORARY` flag with mandatory locking. |
| **Likelihood** | 4 - Probable (Windows is a supported platform per GETTING_STARTED.md) |
| **Consequence** | 3 - Moderate (state file writes fail, compaction tracking breaks) |
| **Risk Score** | **12 (YELLOW)** |
| **Affected Tasks** | TASK-005 |

**Analysis:**

The current `save_state()` (line 277-294) is a simple open-write-close pattern:
```python
with open(state_file, "w", encoding="utf-8") as f:
    json.dump(state, f)
```

The proposed atomic pattern is:
```python
with tempfile.NamedTemporaryFile(...) as tmp:
    json.dump(state, tmp)
    os.replace(tmp.name, str(state_file))
```

On Windows, this has two failure modes:
1. **NamedTemporaryFile locking:** On Windows, `NamedTemporaryFile` opens the file with `O_TEMPORARY` and shares deletion lock. The file cannot be renamed while the context manager holds it open. Solution: Use `delete=False` and manage cleanup manually, or write to a regular temp file.
2. **Target file locking:** If another process (e.g., antivirus, backup software, a concurrent Claude Code session) has the state file open, `os.replace()` will raise `PermissionError` on Windows.

The function already has `except OSError` handling (line 293-294) which will catch Windows `PermissionError` (a subclass of `OSError`), so the graceful degradation is preserved. However, the atomic guarantee is lost on Windows in these edge cases.

**Mitigation Strategy:**
1. Use `tempfile.NamedTemporaryFile(mode='w', dir=state_file.parent, delete=False, suffix='.tmp')` to ensure same-filesystem and explicit cleanup
2. Close the temp file before calling `os.replace()` (critical for Windows compatibility)
3. Wrap `os.replace()` in try/except and clean up the temp file on failure
4. Add explicit comment documenting Windows limitation
5. Use `state_file.parent` as the `dir` argument to `NamedTemporaryFile` to guarantee same-filesystem (avoiding cross-device rename failures)
6. Preserve the existing `except OSError` fallback so that on any failure, the function degrades gracefully

**Residual Risk:** 4 (Likelihood 2 x Consequence 2) - GREEN after implementation with explicit Windows-safe pattern

---

### RSK-EN005-004: tempfile Location Differs Across Platforms

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-EN005-004 |
| **Category** | Code Modification |
| **Description** | `tempfile.NamedTemporaryFile` may create files in a different filesystem than the target state file, causing `os.replace()` to fail with `OSError: [Errno 18] Invalid cross-device link`. |
| **Root Cause** | Default `tempfile` directory (`/tmp` on Linux, `C:\Users\...\AppData\Local\Temp` on Windows) may be on a different mount point or drive than `~/.claude/ecw-statusline-state.json`. |
| **Likelihood** | 1 - Remote (most configurations have HOME and /tmp on same filesystem) |
| **Consequence** | 2 - Marginal (state save fails silently, graceful degradation) |
| **Risk Score** | **2 (GREEN)** |
| **Affected Tasks** | TASK-005 |

**Analysis:**

On most systems, `~/.claude/` and `/tmp` are on the same root filesystem. The risk increases in exotic configurations:
- Network-mounted HOME directories (NFS, SMB)
- Docker volumes where HOME is mapped but /tmp is container-local
- Windows configurations where TEMP is on a different drive than USERPROFILE

However, this risk is fully mitigated by the RSK-EN005-003 mitigation strategy #5: specifying `dir=state_file.parent` in the `NamedTemporaryFile` call, which guarantees the temp file is created on the same filesystem as the target.

**Mitigation Strategy:**
1. Specify `dir=state_file.parent` when creating `NamedTemporaryFile` (eliminates cross-device rename entirely)
2. Ensure `state_file.parent.mkdir(parents=True, exist_ok=True)` is called before temp file creation (already exists at line 290)
3. Existing `except OSError` catch provides graceful degradation for any remaining edge cases

**Residual Risk:** 1 (Likelihood 1 x Consequence 1) - GREEN (fully mitigated by specifying dir parameter)

---

### Category 2: Testing Risks

---

### RSK-EN005-005: New Tests Interfere with Existing Test Suite

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-EN005-005 |
| **Category** | Testing |
| **Description** | The EN-005 tests (`run_no_color_env_test`, `run_use_color_disabled_test`, `run_color_matrix_test`) already exist in `test_statusline.py` (lines 804-1018). These tests manipulate environment variables (`NO_COLOR`) and config files (`ecw-statusline-config.json`) that could leak between tests, causing flaky failures in the existing suite. |
| **Root Cause** | Test isolation relies on manual cleanup in `finally` blocks. Environment variable leakage between test runs within the same process is possible if `env.pop()` or cleanup fails. Config file cleanup uses `unlink(missing_ok=True)` which could silently fail on Windows file locks. |
| **Likelihood** | 4 - Probable (env var/config file side effects are common test issues) |
| **Consequence** | 2 - Marginal (test flakiness, false CI failures, developer confusion) |
| **Risk Score** | **8 (YELLOW)** |
| **Affected Tasks** | TASK-001, TASK-006 |

**Analysis:**

Reviewing the test suite structure:
- Tests use `subprocess.run()` with a copied `env` dictionary (line 248: `env = os.environ.copy()`), which provides process-level isolation for environment variables
- Config files are cleaned up in `finally` blocks (e.g., lines 293-295, 1014-1015)
- The `run_color_matrix_test()` (line 922) runs 4 sub-scenarios in a loop, each modifying `NO_COLOR` and config independently

The subprocess isolation model is actually quite robust -- each test invocation runs `statusline.py` in a fresh process with an explicitly constructed environment. The primary leakage risk is:
1. Config file not cleaned up if a test crashes (OS-level file lock on Windows)
2. Test order dependency if one test's cleanup fails

However, the tests already exist and presumably have been designed for this. The risk is limited to the GREEN phase implementation potentially introducing a code change that alters the test execution behavior (e.g., caching NO_COLOR at import time rather than checking per-invocation).

**Mitigation Strategy:**
1. Verify that `ansi_color()`/`ansi_reset()` check `NO_COLOR` and `use_color` on EVERY invocation (not cached at import time), preserving test isolation via subprocess model
2. Run the full test suite after each code change to catch any ordering issues
3. Ensure all test `finally` blocks properly clean up config files
4. Consider adding a test suite-level cleanup at the start of `main()` to remove any stale config files

**Residual Risk:** 4 (Likelihood 2 x Consequence 2) - GREEN after validating subprocess isolation model works correctly

---

### RSK-EN005-006: Atomic Write Test Reliability

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-EN005-006 |
| **Category** | Testing |
| **Description** | Testing atomic writes is inherently difficult because the atomicity guarantee is about what happens during a crash or concurrent access. A unit test cannot reliably simulate a crash mid-write. Tests may verify the "happy path" without validating the actual atomicity guarantee. |
| **Root Cause** | Atomicity is a system-level property that cannot be fully tested in user-space unit tests. The value of atomic writes is in crash recovery scenarios that are hard to reproduce deterministically. |
| **Likelihood** | 3 - Possible |
| **Consequence** | 1 - Minimal (tests pass but don't fully validate atomicity) |
| **Risk Score** | **3 (GREEN)** |
| **Affected Tasks** | TASK-005 |

**Analysis:**

The atomic write implementation can be validated at several levels:
1. **Functional correctness:** Verify that `save_state()` still correctly persists state (easy to test)
2. **Temp file cleanup:** Verify no orphan temp files remain after `save_state()` completes (testable)
3. **Error handling:** Verify graceful degradation when the target directory is read-only (already tested at line 632)
4. **Atomicity:** Verify that a crash during write leaves either the old state or the new state, never a partial write (hard to test in user-space)

For this implementation scope, levels 1-3 provide sufficient coverage. Level 4 (true atomicity testing) would require OS-level fault injection and is disproportionate to the risk.

**Mitigation Strategy:**
1. Test that `save_state()` produces valid JSON after the write (functional correctness)
2. Test that `save_state()` on a read-only filesystem does not crash (already exists)
3. Test that no temp files remain after `save_state()` completes (new test)
4. Accept that true atomicity is validated by code review, not test execution
5. Add code comment documenting the atomicity guarantee and its Windows limitation

**Residual Risk:** 2 (Likelihood 2 x Consequence 1) - GREEN (acceptable testing coverage)

---

### Category 3: Documentation Risks

---

### RSK-EN005-007: UNC Path Documentation Accuracy

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-EN005-007 |
| **Category** | Documentation |
| **Description** | Documenting UNC path (`\\server\share\...`) limitations without testing them on actual Windows systems risks providing inaccurate guidance. The `pathlib.Path` behavior with UNC paths may differ from documentation assumptions. |
| **Root Cause** | UNC path behavior is documented from code inspection and Python documentation, not from empirical testing. No Windows testing infrastructure is available in the current CI/CD pipeline. |
| **Likelihood** | 3 - Possible |
| **Consequence** | 2 - Marginal (users may follow incorrect workaround advice) |
| **Risk Score** | **6 (YELLOW)** |
| **Affected Tasks** | TASK-002 |

**Analysis:**

The documentation task (TASK-002) must cover:
1. Whether `statusline.py` works when the script itself is on a UNC path
2. Whether `cwd` from Claude Code's JSON payload handles UNC paths
3. Whether the state file path (`~/.claude/ecw-statusline-state.json`) can be on a UNC path
4. Whether `pathlib.Path` correctly resolves UNC paths on Windows

Python's `pathlib` does handle UNC paths (e.g., `PureWindowsPath('//server/share/file')` is valid), but the script uses `os.path.expanduser()` (line 253) which may not interact well with UNC paths as HOME directories.

Since the documentation strategy is adversarial critique cycle, the critics will challenge accuracy claims. The key mitigation is to use hedging language ("may not work", "not tested") rather than definitive claims ("does not work", "will fail").

**Mitigation Strategy:**
1. Use conservative hedging language: "UNC paths have not been tested" rather than "UNC paths do not work"
2. Document known Python stdlib behavior with UNC paths based on CPython documentation
3. Recommend mapped drives as a workaround (safe, tested recommendation)
4. Mark UNC path support as "Not Tested" in the platform support table
5. Rely on adversarial critique cycle to challenge any inaccurate claims

**Residual Risk:** 3 (Likelihood 1 x Consequence 3) - GREEN after conservative documentation approach

---

### RSK-EN005-008: SSH/tmux Compatibility Claims Untested

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-EN005-008 |
| **Category** | Documentation |
| **Description** | Documenting SSH and tmux terminal compatibility without verification risks providing guidance that fails in practice. Terminal capability negotiation over SSH and tmux multiplexing both alter TERM variable behavior and ANSI rendering. |
| **Root Cause** | SSH and tmux introduce terminal abstraction layers that modify ANSI escape sequence handling. Documentation is based on general knowledge, not empirical testing with this specific script. |
| **Likelihood** | 3 - Possible |
| **Consequence** | 2 - Marginal (users unable to use tool in SSH/tmux as documented) |
| **Risk Score** | **6 (YELLOW)** |
| **Affected Tasks** | TASK-004 |

**Analysis:**

Key SSH/tmux issues for ANSI 256-color output:
1. **SSH:** Terminal capabilities are negotiated via TERM variable. If `TERM=dumb` or `TERM=vt100`, ANSI 256-color codes will not render correctly.
2. **tmux:** Requires `tmux -2` or `set -g default-terminal "tmux-256color"` for 256-color support. Without this, colors degrade to 8-color mode.
3. **Screen:** Similar to tmux but with `screen-256color` TERM type.
4. **Mosh:** May have different ANSI handling than SSH.

The script does not check TERM variable or terminal capabilities -- it unconditionally emits `\033[38;5;{code}m` escape sequences. This means:
- In SSH with proper TERM: Works correctly
- In SSH with TERM=dumb: Garbled output with visible escape codes
- In tmux with 256-color: Works correctly
- In tmux without 256-color: Colors may be wrong but not garbled

The documentation should focus on what users need to configure, not on what the script detects.

**Mitigation Strategy:**
1. Document TERM variable requirements explicitly (`xterm-256color`, `screen-256color`, `tmux-256color`)
2. Provide tmux configuration snippet for 256-color mode
3. Recommend `NO_COLOR=1` or `use_color: false` as fallback for problematic SSH/tmux sessions
4. Use advisory language: "If colors appear incorrect in SSH/tmux, try these steps..."
5. Rely on adversarial critique cycle to validate documentation completeness

**Residual Risk:** 3 (Likelihood 1 x Consequence 3) - GREEN after documentation with practical workarounds

---

### Category 4: Integration Risks

---

### RSK-EN005-009: Config Schema Backward Compatibility

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-EN005-009 |
| **Category** | Integration |
| **Description** | Adding `use_color` to the `display` section of `DEFAULT_CONFIG` could conflict with existing user config files that have a `display` section. If a user's config has `"display": {"compact_mode": true}`, the deep merge behavior must correctly add `use_color: true` as a default without overwriting user settings. |
| **Root Cause** | Config loading uses a deep merge strategy (user config overrides defaults). Adding a new key to defaults is safe IF the merge is additive. But if the merge replaces entire sections, existing user customizations could be lost. |
| **Likelihood** | 2 - Unlikely |
| **Consequence** | 2 - Marginal (user's existing config continues working, just missing new option) |
| **Risk Score** | **4 (GREEN)** |
| **Affected Tasks** | TASK-006 |

**Analysis:**

Reviewing the config loading logic (line 165+), the script uses `_get_config_paths()` to find config files and merges them into `DEFAULT_CONFIG`. The merge behavior determines the risk level:
- **Additive merge (key-level):** New `use_color` key is added to defaults, user config overrides only keys it specifies. Safe.
- **Replace merge (section-level):** User's `"display": {"compact_mode": true}` replaces the entire `display` section, losing `use_color` default. Risky.

The existing config system already handles keys like `use_emoji` (line 67) in the `display` section, and the test for `compact_mode` (line 354) works correctly with partial config overrides. This indicates the merge is additive at the key level, not section-level replacement.

**Mitigation Strategy:**
1. Verify the config merge is key-level (not section-level) by reviewing the merge function
2. Add `use_color` with default value `True` to `DEFAULT_CONFIG["display"]` to match existing color-enabled behavior
3. Test with a partial config `{"display": {"compact_mode": true}}` to verify `use_color` defaults to `True`
4. No user migration needed since the default value preserves existing behavior

**Residual Risk:** 2 (Likelihood 1 x Consequence 2) - GREEN (config merge is additive)

---

### RSK-EN005-010: NO_COLOR Standard Compliance Edge Cases

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-EN005-010 |
| **Category** | Integration |
| **Description** | The `no-color.org` standard specifies that the *presence* of `NO_COLOR` matters, not its value. This means `NO_COLOR=""` (empty string) should disable colors. A common implementation mistake is to use `os.environ.get("NO_COLOR")` with a truthiness check, which treats empty string as falsy (colors would remain enabled). |
| **Root Cause** | Python's truthiness semantics: `bool("") == False` but `("" is not None) == True`. The standard requires presence-checking, not value-checking. |
| **Likelihood** | 3 - Possible (common implementation mistake) |
| **Consequence** | 2 - Marginal (non-compliance with standard, functional but incorrect) |
| **Risk Score** | **6 (YELLOW)** |
| **Affected Tasks** | TASK-001 |

**Analysis:**

The `no-color.org` specification states:

> "When set, callers should not add ANSI color escape codes to command output. Regardless of whether it's set to a truthy or falsy value, the presence of the variable should be enough."

The correct Python implementation is:
```python
# CORRECT: checks presence, not value
if os.environ.get("NO_COLOR") is not None:
    return ""

# INCORRECT: treats NO_COLOR="" as falsy
if os.environ.get("NO_COLOR"):
    return ""
```

The existing test `run_no_color_env_test()` (line 818) sets `env["NO_COLOR"] = "1"` which would pass with either implementation. A robust test should also check `NO_COLOR=""`.

**Mitigation Strategy:**
1. Use `os.environ.get("NO_COLOR") is not None` explicitly in the implementation
2. Add a test case for `NO_COLOR=""` (empty string) in the color matrix test
3. Add code comment citing the `no-color.org` specification
4. Consider also testing `NO_COLOR=0` and `NO_COLOR=false` to ensure presence-only semantics

**Residual Risk:** 2 (Likelihood 1 x Consequence 2) - GREEN after explicit `is not None` check and edge case test

---

## L2: Traceability

### EN-005 Risks to XPLAT-001 Risk Register Mapping

| EN-005 Risk | XPLAT-001 Risk | Relationship |
|-------------|----------------|--------------|
| RSK-EN005-001 (NO_COLOR + use_color) | RSK-XPLAT-012 (NO_COLOR Standard, 10 YELLOW) | **Implements mitigation.** EN-005 TASK-001 + TASK-006 directly mitigate RSK-XPLAT-012. Successful implementation reduces RSK-XPLAT-012 to residual score 1 (GREEN). |
| RSK-EN005-002 (ansi_color regression) | RSK-XPLAT-008 (ANSI Color Support Varies, 12 YELLOW) | **Partially related.** Both involve ANSI color behavior. RSK-XPLAT-008 mitigation "add config option for color disable" is fulfilled by TASK-006 (use_color). |
| RSK-EN005-003 (os.replace cross-platform) | RSK-XPLAT-022 (State File Corruption, 8 YELLOW) | **Implements mitigation.** EN-005 TASK-005 directly implements the "atomic write" long-term mitigation for RSK-XPLAT-022. Successful implementation reduces RSK-XPLAT-022 to residual score 2 (GREEN). |
| RSK-EN005-004 (tempfile location) | RSK-XPLAT-022 (State File Corruption, 8 YELLOW) | **Subsidiary risk.** Same parent risk, different failure mode. |
| RSK-EN005-005 (test interference) | RSK-XPLAT-007 (CI/CD Pipeline, 15 RED) | **Tangentially related.** Test reliability affects CI/CD pipeline reliability. |
| RSK-EN005-006 (atomic write test) | RSK-XPLAT-022 (State File Corruption, 8 YELLOW) | **Testing completeness.** Tests cannot fully validate atomicity. |
| RSK-EN005-007 (UNC path docs accuracy) | None directly | **New documentation risk.** UNC paths were gap G-017 but had no explicit risk in XPLAT-001. |
| RSK-EN005-008 (SSH/tmux docs accuracy) | RSK-XPLAT-008 (ANSI Color Support Varies, 12 YELLOW) | **Partially related.** SSH/tmux terminal ANSI support is a subset of the broader ANSI compatibility issue. |
| RSK-EN005-009 (config backward compat) | RSK-XPLAT-020 (No Upgrade Path, 12 YELLOW) | **Partially related.** Config schema changes affect upgrade path. |
| RSK-EN005-010 (NO_COLOR edge cases) | RSK-XPLAT-012 (NO_COLOR Standard, 10 YELLOW) | **Refines parent risk.** Specific implementation edge case within the broader NO_COLOR standard compliance. |

### Risk-to-Task-to-Batch Mapping

| Risk ID | Score | Affected Task(s) | Batch | Phase |
|---------|-------|-------------------|-------|-------|
| RSK-EN005-001 | 9 YELLOW | TASK-001, TASK-006 | A | RED (Phase 1), GREEN (Phase 2) |
| RSK-EN005-002 | 6 YELLOW | TASK-001, TASK-006 | A | GREEN (Phase 2) |
| RSK-EN005-003 | 12 YELLOW | TASK-005 | B | GREEN (Phase 2) |
| RSK-EN005-004 | 2 GREEN | TASK-005 | B | GREEN (Phase 2) |
| RSK-EN005-005 | 8 YELLOW | TASK-001, TASK-006 | A | RED (Phase 1), GREEN (Phase 2) |
| RSK-EN005-006 | 3 GREEN | TASK-005 | B | RED (Phase 1), GREEN (Phase 2) |
| RSK-EN005-007 | 6 YELLOW | TASK-002 | C | GREEN (Phase 2) |
| RSK-EN005-008 | 6 YELLOW | TASK-004 | C | GREEN (Phase 2) |
| RSK-EN005-009 | 4 GREEN | TASK-006 | A | GREEN (Phase 2) |
| RSK-EN005-010 | 6 YELLOW | TASK-001 | A | RED (Phase 1), GREEN (Phase 2) |

### Batch-Level Risk Aggregation

| Batch | Tasks | Risk Count | Highest Risk | Aggregate Profile |
|-------|-------|------------|-------------|-------------------|
| **Batch A** (Color/ANSI) | TASK-001, TASK-006 | 5 risks | RSK-EN005-001 (9 YELLOW) | **MODERATE** - Highest concentration of risks. Interaction complexity between NO_COLOR and use_color drives risk. TDD approach with pre-existing test infrastructure (lines 804-1018) provides strong mitigation. |
| **Batch B** (Atomic Writes) | TASK-005 | 3 risks | RSK-EN005-003 (12 YELLOW) | **MODERATE** - Highest individual risk score (12). Cross-platform `os.replace()` behavior is the primary concern. Existing graceful degradation (`except OSError`) provides safety net. |
| **Batch C** (Documentation) | TASK-002, TASK-003, TASK-004 | 2 risks | RSK-EN005-007 (6 YELLOW) | **LOW** - Documentation-only risks. Adversarial critique cycle provides quality assurance. Conservative hedging language mitigates accuracy concerns. |

### Risk Mitigation Priority Ranking

| Priority | Risk ID | Score | Mitigation Action | Implementation Phase | Effort |
|----------|---------|-------|-------------------|---------------------|--------|
| 1 | RSK-EN005-003 | 12 YELLOW | Use `dir=state_file.parent` + `delete=False` + close-before-replace pattern | GREEN Phase (Batch B) | Embedded in TASK-005 |
| 2 | RSK-EN005-001 | 9 YELLOW | Implement `is not None` check for NO_COLOR; 4-scenario matrix test | RED Phase (tests) + GREEN Phase (impl) | Embedded in TASK-001/006 |
| 3 | RSK-EN005-005 | 8 YELLOW | Validate subprocess isolation; run full suite after each change | Continuous throughout | 15 min per validation |
| 4 | RSK-EN005-010 | 6 YELLOW | Add empty-string NO_COLOR test case; use `is not None` | RED Phase (test) + GREEN Phase (impl) | Embedded in TASK-001 |
| 5 | RSK-EN005-002 | 6 YELLOW | Guard clause pattern (early return in ansi_color/ansi_reset) | GREEN Phase (Batch A) | Embedded in TASK-001/006 |
| 6 | RSK-EN005-007 | 6 YELLOW | Conservative hedging language in UNC docs | GREEN Phase (Batch C) | Embedded in TASK-002 |
| 7 | RSK-EN005-008 | 6 YELLOW | Practical workarounds in SSH/tmux docs | GREEN Phase (Batch C) | Embedded in TASK-004 |
| 8 | RSK-EN005-009 | 4 GREEN | Verify additive config merge behavior | GREEN Phase (Batch A) | 10 min verification |
| 9 | RSK-EN005-006 | 3 GREEN | Test functional correctness + cleanup, accept atomicity by code review | GREEN Phase (Batch B) | Embedded in TASK-005 |
| 10 | RSK-EN005-004 | 2 GREEN | Mitigated by RSK-EN005-003 mitigation (dir parameter) | GREEN Phase (Batch B) | No additional effort |

### Monitoring Indicators for TDD Workflow

| Indicator | Threshold | Action | Phase |
|-----------|-----------|--------|-------|
| **RED Phase test count** | >= 3 new tests (NO_COLOR, use_color, matrix) | Tests already exist in suite; verify they fail before GREEN | Phase 1 |
| **GREEN Phase regression count** | 0 existing test failures | Any existing test failure = STOP, diagnose before continuing | Phase 2 |
| **Full suite pass rate** | 100% (all 20+ tests) | Must be 100% after each code change; any failure triggers investigation | Continuous |
| **Config merge validation** | `use_color` default resolves to `True` with partial user config | Test with `{"display": {"compact_mode": true}}` config | Phase 2 |
| **Temp file cleanup** | 0 orphan `.tmp` files in state directory after test suite | Check `~/.claude/` for `*.tmp` files after test run | Phase 2 |
| **NO_COLOR empty string** | `NO_COLOR=""` disables colors | Must be included in test matrix | Phase 1 (RED) |
| **os.replace fallback** | `save_state()` on read-only FS still produces status output | Existing `run_readonly_state_test()` must pass | Phase 2 |
| **Adversarial critique score** | >= 0.92 weighted rubric | If < 0.92, iterate (max 3 times) | Phase 3 |
| **Documentation hedging language** | No unverified definitive claims in UNC/SSH docs | Critique should flag any "will", "always", "never" claims about untested scenarios | Phase 3 |

---

## Appendix A: Risk Scoring Reference

### Likelihood Definitions (NPR 8000.4C)

| Score | Level | Description |
|-------|-------|-------------|
| 1 | Remote | Very unlikely to occur (< 5% probability) |
| 2 | Unlikely | Not expected but possible (5-25% probability) |
| 3 | Possible | May occur sometime (25-50% probability) |
| 4 | Probable | Will probably occur (50-75% probability) |
| 5 | Near Certain | Expected to occur (> 75% probability) |

### Consequence Definitions (NPR 8000.4C)

| Score | Level | Description |
|-------|-------|-------------|
| 1 | Minimal | Negligible impact; workaround available |
| 2 | Marginal | Minor impact; some user inconvenience |
| 3 | Moderate | Significant impact; feature degradation |
| 4 | Significant | Major impact; core functionality affected |
| 5 | Catastrophic | Complete failure; data loss or security issue |

### Risk Level Thresholds

| Score Range | Level | Action Required |
|-------------|-------|-----------------|
| 1-5 | GREEN | Accept with monitoring |
| 6-12 | YELLOW | Mitigate during implementation |
| 15-25 | RED | Block implementation until resolved |

---

## Appendix B: Key Code References

| Reference | File | Line(s) | Relevance |
|-----------|------|---------|-----------|
| `ansi_color()` | statusline.py | 302-306 | Primary modification target for TASK-001, TASK-006 |
| `ansi_reset()` | statusline.py | 309-311 | Secondary modification target for TASK-001, TASK-006 |
| `save_state()` | statusline.py | 277-294 | Primary modification target for TASK-005 |
| `DEFAULT_CONFIG` | statusline.py | 61-159 | Config schema target for TASK-006 (add `use_color`) |
| `_resolve_state_path()` | statusline.py | 246-256 | State file path resolution (context for TASK-005) |
| `load_state()` | statusline.py | 259-274 | State loading (context for TASK-005 testing) |
| `_get_config_paths()` | statusline.py | 165-169 | Config loading (context for TASK-006 backward compat) |
| `run_no_color_env_test()` | test_statusline.py | 804-855 | Existing test for TASK-001 |
| `run_use_color_disabled_test()` | test_statusline.py | 858-919 | Existing test for TASK-006 |
| `run_color_matrix_test()` | test_statusline.py | 922-1018 | Existing integration test for TASK-001 + TASK-006 |
| `run_readonly_state_test()` | test_statusline.py | 632-689 | Existing test validating graceful degradation |
| `GETTING_STARTED.md` | GETTING_STARTED.md | Full file | Documentation target for TASK-002, TASK-003, TASK-004 |
| `git_timeout: 2` | statusline.py | 156 | Already-implemented config (TASK-003 needs docs only) |

---

*Risk assessment generated by nse-risk agent v1.0.0*
*Based on NASA NPR 8000.4C 5x5 Risk Matrix methodology*
*Date: 2026-02-11*
