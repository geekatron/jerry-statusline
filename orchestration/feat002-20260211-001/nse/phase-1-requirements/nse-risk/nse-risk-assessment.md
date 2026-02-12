# Risk Assessment: FEAT-002 High-Priority Improvements

**Project:** jerry-statusline (ECW Status Line v2.1.0)
**Feature:** FEAT-002 - High-Priority Improvements (Phase 2)
**Assessment Date:** 2026-02-11
**Agent:** nse-risk v2.1.0
**Methodology:** NASA NPR 7123.1D Process 13 (5x5 Risk Matrix)

---

## Executive Summary

This risk assessment identifies and scores **12 risks** for the remaining implementation work in FEAT-002 (High-Priority Improvements). The assessment focuses on EN-003 (Code Hardening) and EN-004 (Documentation Completion).

### Risk Profile Overview

| Category | Critical (RED) | High (YELLOW) | Medium (GREEN) | Total |
|----------|----------------|---------------|----------------|-------|
| Implementation | 0 | 4 | 2 | 6 |
| Testing | 0 | 2 | 1 | 3 |
| Documentation | 0 | 1 | 2 | 3 |
| **Total** | **0** | **7** | **5** | **12** |

**Key Finding:** No critical (RED) risks identified. All risks are manageable with proper mitigation before GA release.

### Risk Distribution

- **GREEN (1-5):** 5 risks - Accept with monitoring
- **YELLOW (6-12):** 7 risks - Mitigate before GA
- **RED (15-25):** 0 risks - None identified

### Context

FEAT-002 builds on the successful completion of FEAT-001 (Critical Remediations), which delivered:
- ✅ CI/CD pipeline running on ubuntu-latest, macos-latest, windows-latest
- ✅ Python 3.9-3.12 compatibility verified
- ✅ Windows native support validated
- ✅ Alpine Linux exclusion documented

**Already Mitigated Risks:**
- RSK-XPLAT-001: Windows native support untested → MITIGATED by EN-002
- RSK-XPLAT-003: Alpine Linux incompatibility → MITIGATED by EN-002 documentation
- RSK-XPLAT-007: CI/CD not implemented → MITIGATED by EN-001

---

## Risk Heat Map (5x5 Matrix)

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
     |              R-005       R-003
     |              R-010       R-006
     |                          R-011
-----+--------------------------------------------------------------------
  3  |     3           6           9           12             15
Poss |   (Green)    (Yellow)    (Yellow)    (Yellow)         (Red)
     |   R-012      R-002       R-007
     |              R-009       R-008
     |
-----+--------------------------------------------------------------------
  2  |     2           4           6            8             10
Unlik|   (Green)    (Green)     (Yellow)    (Yellow)       (Yellow)
     |   R-004                  R-001
     |
-----+--------------------------------------------------------------------
  1  |     1           2           3            4              5
Remot|   (Green)    (Green)     (Green)      (Green)        (Green)
     |
-----+--------------------------------------------------------------------
LIKELIHOOD
```

**Legend:**
- **GREEN (1-5):** Accept risk with monitoring
- **YELLOW (6-12):** Mitigate risk before GA release
- **RED (15-25):** Critical - Block deployment until resolved

---

## Risk Register

### Category 1: Implementation Risks

---

#### R-001: Subprocess Encoding Hardening Incomplete

| Attribute | Value |
|-----------|-------|
| **Risk ID** | R-001 |
| **Category** | Implementation |
| **Description** | Adding `encoding='utf-8'` to subprocess calls may break systems with non-UTF8 locales (LANG=C, POSIX, legacy Windows). Git output may fail to decode on systems with different default encodings. |
| **Root Cause** | Python subprocess behavior varies by locale; forcing UTF-8 may cause UnicodeDecodeError on systems expecting ASCII or other encodings |
| **Likelihood** | 2 - Unlikely |
| **Consequence** | 3 - Moderate |
| **Risk Score** | **6 (YELLOW)** |
| **Evidence** | XPLAT-001 e-008 RSK-026: "Non-UTF8 system locale: LANG=C or legacy Windows locales" |

**Potential Impact:**
- Git subprocess calls fail with UnicodeDecodeError on non-UTF8 systems
- Git segment silently disappears without explanation
- Status line breaks on older Linux distributions with C locale
- Windows systems with non-Unicode codepages affected

**Mitigation Strategy:**

1. **Immediate** (Before implementation):
   - Add encoding='utf-8' with errors='replace' fallback
   - Test on system with LANG=C locale
   - Test on Windows with non-Unicode codepage

2. **Short-term** (During implementation):
   ```python
   subprocess.run(
       ["git", "rev-parse", "--abbrev-ref", "HEAD"],
       capture_output=True,
       encoding='utf-8',
       errors='replace',  # Critical: fallback for invalid UTF-8
       timeout=timeout,
   )
   ```

3. **Long-term** (Post-implementation):
   - Document locale requirements in GETTING_STARTED.md
   - Add debug logging when encoding errors occur

**Residual Risk After Mitigation:**

| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 1 - Remote | 2 - Marginal | **2 (GREEN)** |

**Risk Owner:** Development Team
**Target Resolution:** Before TASK-001 completion
**Monitoring:** CI/CD test results; locale-specific testing

---

#### R-002: Missing HOME Variable Edge Cases

| Attribute | Value |
|-----------|-------|
| **Risk ID** | R-002 |
| **Category** | Implementation |
| **Description** | Wrapping `Path.home()` in try/except may not cover all edge cases. State file and config file operations could fail in Docker containers, minimal environments, or when HOME is set to invalid/inaccessible path. |
| **Root Cause** | Multiple failure modes: HOME not set, HOME invalid, HOME not readable, HOME filesystem read-only |
| **Likelihood** | 3 - Possible |
| **Consequence** | 2 - Marginal |
| **Risk Score** | **6 (YELLOW)** |
| **Evidence** | Code lines 242-252: `_resolve_state_path()` handles missing HOME; Config loading lines 161-169 handles missing HOME |

**Potential Impact:**
- State file operations fail silently in Docker containers
- Compaction detection becomes non-functional without user awareness
- Config file not loaded in environments without HOME
- No graceful degradation messaging to user

**Mitigation Strategy:**

1. **Immediate** (Before implementation):
   - Verify current code already handles most cases (lines 161-169, 242-252)
   - Test in Docker container with no HOME set
   - Test with HOME pointing to non-existent directory
   - Test with HOME pointing to read-only directory

2. **Short-term** (During implementation):
   - Add environment variable fallback: ECW_STATE_DIR, ECW_CONFIG_DIR
   - Document required environment variables for containerized deployments
   - Add one-time warning in debug mode when HOME unavailable

3. **Long-term** (Post-implementation):
   - Add container deployment guide (already planned in EN-004 TASK-001)

**Residual Risk After Mitigation:**

| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 2 - Unlikely | 1 - Minimal | **2 (GREEN)** |

**Risk Owner:** Development Team
**Target Resolution:** Before TASK-002 completion
**Monitoring:** Docker container testing; CI/CD logs

---

#### R-003: ASCII Emoji Fallback Incomplete Coverage

| Attribute | Value |
|-----------|-------|
| **Risk ID** | R-003 |
| **Category** | Implementation |
| **Description** | Implementing complete ASCII fallback for all emoji characters requires identifying every Unicode character used and providing ASCII alternatives. Missing even one character will cause display issues on terminals without emoji support. |
| **Root Cause** | Emoji scattered throughout codebase in 8 segments; no comprehensive inventory exists |
| **Likelihood** | 4 - Probable |
| **Consequence** | 3 - Moderate |
| **Risk Score** | **12 (YELLOW)** |
| **Evidence** | Code analysis shows emoji in: Model icons (🔵🟣🟢), Context (📊), Cost (💰), Tokens (⚡), Session (⏱️), Compaction (📉), Tools (🔧), Git (🌿), Directory (📂), Progress bar (▓░), Status indicators (✓●), Token arrows (→↺) |

**Potential Impact:**
- Some emoji remain even when use_emoji=false
- Progress bar characters (▓░) appear as mojibake on ASCII-only terminals
- Token arrows (→↺) may not have ASCII alternatives
- Status line becomes unreadable on legacy terminals (cmd.exe, PuTTY with ASCII)
- User perception of broken software

**Complete Emoji Inventory:**

| Segment | Unicode Characters | ASCII Fallback Needed |
|---------|-------------------|----------------------|
| Model | 🔵🟣🟢⚪ | [O][S][H][?] |
| Context | 📊 | [=] |
| Cost | 💰 | $ |
| Tokens | ⚡→↺ | ! -> @ |
| Session | ⏱️ | [T] |
| Compaction | 📉 | [v] or DOWN |
| Tools | 🔧 | [W] |
| Git | 🌿 | [G] |
| Directory | 📂 | [D] |
| Progress | ▓░ | #- or =. |
| Git Status | ✓● | + * |

**Mitigation Strategy:**

1. **Immediate** (Before implementation):
   - Create complete emoji inventory (see table above)
   - Audit all format strings for Unicode characters
   - Test with use_emoji=false on Windows cmd.exe
   - Test with TERM=dumb environment

2. **Short-term** (During implementation):
   - Create lookup function for all symbols:
   ```python
   def get_symbol(name: str, config: Dict) -> str:
       if config["display"]["use_emoji"]:
           return EMOJI_SYMBOLS[name]
       return ASCII_SYMBOLS[name]
   ```
   - Define both dictionaries comprehensively
   - Replace all hardcoded emoji with get_symbol() calls

3. **Long-term** (Post-implementation):
   - Add automated test with use_emoji=false
   - Verify no Unicode characters > U+007F in ASCII mode output

**Residual Risk After Mitigation:**

| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 1 - Remote | 2 - Marginal | **2 (GREEN)** |

**Risk Owner:** Development Team
**Target Resolution:** Before TASK-003 completion
**Monitoring:** CI/CD test with ASCII-only mode; visual inspection

---

#### R-004: Backward Compatibility Break

| Attribute | Value |
|-----------|-------|
| **Risk ID** | R-004 |
| **Category** | Implementation |
| **Description** | Code changes in EN-003 may introduce breaking changes for existing users (config format, output format, state file format). No migration guide exists for v2.0.0 to v2.1.0 users. |
| **Root Cause** | Version management not prioritized; no changelog tracking |
| **Likelihood** | 2 - Unlikely |
| **Consequence** | 2 - Marginal |
| **Risk Score** | **4 (GREEN)** |
| **Evidence** | XPLAT-001 e-008 RSK-020: "No upgrade path documentation"; No CHANGELOG.md exists |

**Potential Impact:**
- Existing users' configurations break after code update
- State file format incompatibility causes compaction detection to fail
- Emoji fallback changes visual appearance unexpectedly
- User confusion and support burden

**Mitigation Strategy:**

1. **Immediate** (Before implementation):
   - Document all intended changes in EN-003 and EN-004
   - Review config schema for breaking changes
   - Identify any state file format changes

2. **Short-term** (During implementation):
   - Maintain backward compatibility for config file
   - Add version field to state file for future migration
   - Test with existing v2.1.0 config files

3. **Long-term** (Post-implementation):
   - Create CHANGELOG.md (planned in EN-004 TASK-007)
   - Document migration path if needed

**Residual Risk After Mitigation:**

| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 1 - Remote | 1 - Minimal | **1 (GREEN)** |

**Risk Owner:** Development Team
**Target Resolution:** Before FEAT-002 completion
**Monitoring:** User upgrade reports; GitHub issues

---

#### R-005: Code Changes Introduce Regressions

| Attribute | Value |
|-----------|-------|
| **Risk ID** | R-005 |
| **Category** | Implementation |
| **Description** | Adding encoding parameters, HOME handling, and emoji fallback logic may introduce bugs in existing functionality. Current test suite has limited coverage and may not catch regressions. |
| **Root Cause** | Manual changes to production code without comprehensive regression testing; test_statusline.py covers 12 functional tests but may miss edge cases |
| **Likelihood** | 4 - Probable |
| **Consequence** | 2 - Marginal |
| **Risk Score** | **8 (YELLOW)** |
| **Evidence** | test_statusline.py has 12 tests but no specific tests for: encoding handling, HOME variable edge cases, emoji fallback modes |

**Potential Impact:**
- Git segment stops working on some platforms
- State file operations break in normal environments
- Performance degradation from additional error handling
- Existing users experience functionality loss

**Mitigation Strategy:**

1. **Immediate** (Before implementation):
   - Run full test suite before any changes (baseline)
   - Review test coverage for affected code paths
   - Identify gaps in test coverage

2. **Short-term** (During implementation):
   - Add new test cases for each change:
     - Test with encoding='utf-8' and errors='replace'
     - Test with HOME not set
     - Test with use_emoji=false (verify no Unicode)
   - Run tests on all 3 platforms (ubuntu, macos, windows) via CI/CD
   - Manual regression testing on VS Code terminal

3. **Long-term** (Post-implementation):
   - Expand test suite to cover new edge cases
   - Consider code coverage metrics in CI/CD

**Residual Risk After Mitigation:**

| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 2 - Unlikely | 2 - Marginal | **4 (GREEN)** |

**Risk Owner:** Development Team
**Target Resolution:** Throughout EN-003 implementation
**Monitoring:** CI/CD test results; manual testing reports

---

#### R-006: VS Code Terminal Compatibility Issues

| Attribute | Value |
|-----------|-------|
| **Risk ID** | R-006 |
| **Category** | Implementation |
| **Description** | VS Code integrated terminal has known ANSI color rendering differences. Code hardening changes may work on standard terminals but fail in VS Code, the primary environment for Claude Code users. |
| **Root Cause** | VS Code terminal not tested despite being high-exposure environment; different ANSI escape sequence handling |
| **Likelihood** | 4 - Probable |
| **Consequence** | 3 - Moderate |
| **Risk Score** | **12 (YELLOW)** |
| **Evidence** | XPLAT-001 e-008 RSK-011: "VS Code integrated terminal has known 256-color rendering issues. Since Claude Code users likely use VS Code, this is a high-exposure environment." |

**Potential Impact:**
- Colors appear different than intended in VS Code
- Progress bar characters render incorrectly
- Emoji fallback mode still shows broken characters
- ASCII mode has unexpected display issues
- Primary user base affected (Claude Code users)

**Mitigation Strategy:**

1. **Immediate** (Before TASK-004):
   - Test current v2.1.0 in VS Code terminal on all 3 platforms
   - Document baseline behavior
   - Identify known issues

2. **Short-term** (During TASK-004):
   - Test all emoji modes (enabled/disabled) in VS Code
   - Test ANSI colors in VS Code on macOS, Linux, Windows
   - Test progress bar rendering
   - Test with different VS Code terminal.integrated.fontFamily settings
   - Document recommended VS Code settings if needed

3. **Long-term** (Post-implementation):
   - Add VS Code terminal testing to manual test checklist
   - Document VS Code-specific configuration in GETTING_STARTED.md

**Residual Risk After Mitigation:**

| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 2 - Unlikely | 2 - Marginal | **4 (GREEN)** |

**Risk Owner:** Development Team
**Target Resolution:** TASK-004 completion
**Monitoring:** VS Code user feedback; manual testing

---

### Category 2: Testing Risks

---

#### R-007: Non-UTF8 Locale Testing Insufficient

| Attribute | Value |
|-----------|-------|
| **Risk ID** | R-007 |
| **Category** | Testing |
| **Description** | Testing encoding changes requires systems with LANG=C or POSIX locales. Current CI/CD matrix uses default UTF-8 locales on all runners, missing edge cases. |
| **Root Cause** | GitHub Actions runners default to UTF-8 locale; manual locale configuration not included in test matrix |
| **Likelihood** | 3 - Possible |
| **Consequence** | 3 - Moderate |
| **Risk Score** | **9 (YELLOW)** |
| **Evidence** | .github/workflows/test.yml runs on standard GitHub runners with default locales; no LANG=C testing |

**Potential Impact:**
- Encoding bugs slip through CI/CD
- Production failures on systems with C locale
- Git subprocess calls fail on legacy Linux distributions
- Silent failures with no debug output

**Mitigation Strategy:**

1. **Immediate** (Before TASK-001):
   - Add locale testing to CI/CD matrix:
   ```yaml
   - name: Test with C locale
     env:
       LANG: C
       LC_ALL: C
     run: uv run python test_statusline.py
   ```

2. **Short-term** (During testing):
   - Manual testing on Ubuntu with LANG=C
   - Manual testing on Windows with non-Unicode codepage
   - Test git subprocess output with non-ASCII branch names

3. **Long-term** (Post-implementation):
   - Document locale requirements in GETTING_STARTED.md
   - Add locale troubleshooting section

**Residual Risk After Mitigation:**

| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 2 - Unlikely | 2 - Marginal | **4 (GREEN)** |

**Risk Owner:** Development Team
**Target Resolution:** Before EN-003 completion
**Monitoring:** CI/CD test matrix; user locale reports

---

#### R-008: Docker Container Testing Not Automated

| Attribute | Value |
|-----------|-------|
| **Risk ID** | R-008 |
| **Category** | Testing |
| **Description** | HOME variable handling and read-only filesystem scenarios are best tested in Docker containers, but CI/CD has no container testing. Manual Docker testing may be inconsistent or skipped. |
| **Root Cause** | Container scenarios not prioritized in CI/CD; focus on native platform testing |
| **Likelihood** | 3 - Possible |
| **Consequence** | 3 - Moderate |
| **Risk Score** | **9 (YELLOW)** |
| **Evidence** | XPLAT-001 e-008 RSK-004: "Docker containers typically lack TTY, causing os.get_terminal_size() to always fail. Git may not be installed. HOME environment may not be set." |

**Potential Impact:**
- Container deployment issues not discovered until user reports
- HOME variable handling bugs slip through testing
- State file operations fail in containerized environments
- Documentation of container deployment inaccurate

**Mitigation Strategy:**

1. **Immediate** (Before TASK-002):
   - Add manual Docker testing to checklist:
   ```bash
   docker run --rm -i python:3.11-slim /bin/bash -c \
     "unset HOME && python3 statusline.py < test_payload.json"
   ```

2. **Short-term** (During testing):
   - Test with HOME not set
   - Test with HOME pointing to /tmp (writeable)
   - Test with HOME pointing to / (read-only for user)
   - Test in python:3.11-slim container (no git installed)

3. **Long-term** (Post-implementation):
   - Consider adding Docker test to CI/CD matrix
   - Document container deployment requirements (EN-004 TASK-001)

**Residual Risk After Mitigation:**

| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 2 - Unlikely | 2 - Marginal | **4 (GREEN)** |

**Risk Owner:** Development Team
**Target Resolution:** Before EN-003 completion
**Monitoring:** Container deployment feedback; manual test results

---

#### R-009: Manual Testing Checklist Incomplete

| Attribute | Value |
|-----------|-------|
| **Risk ID** | R-009 |
| **Category** | Testing |
| **Description** | EN-003 TASK-004 requires manual VS Code terminal testing. Without a comprehensive checklist, testing may miss edge cases or be inconsistent across platforms. |
| **Root Cause** | No standardized manual testing procedure; ad-hoc testing approach |
| **Likelihood** | 3 - Possible |
| **Consequence** | 2 - Marginal |
| **Risk Score** | **6 (YELLOW)** |
| **Evidence** | FEAT-002 acceptance criteria includes manual VS Code testing but no testing procedure defined |

**Potential Impact:**
- Inconsistent testing across macOS, Linux, Windows
- VS Code-specific issues discovered post-release
- Testing time longer than estimated (2h)
- Incomplete test coverage of emoji modes and color schemes

**Mitigation Strategy:**

1. **Immediate** (Before TASK-004):
   - Create comprehensive VS Code testing checklist:
     - [ ] Test on macOS VS Code with default terminal
     - [ ] Test on Linux VS Code with default terminal
     - [ ] Test on Windows VS Code with PowerShell
     - [ ] Test on Windows VS Code with Git Bash
     - [ ] Test with use_emoji=true
     - [ ] Test with use_emoji=false
     - [ ] Test progress bar rendering
     - [ ] Test ANSI 256-color support
     - [ ] Test with dark theme
     - [ ] Test with light theme
     - [ ] Test with different font families (Monospace, Consolas, etc.)

2. **Short-term** (During TASK-004):
   - Execute checklist systematically
   - Document results for each configuration
   - Capture screenshots for visual verification

3. **Long-term** (Post-implementation):
   - Add manual testing procedure to project documentation
   - Consider automation if feasible

**Residual Risk After Mitigation:**

| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 1 - Remote | 2 - Marginal | **2 (GREEN)** |

**Risk Owner:** Development Team
**Target Resolution:** Before TASK-004 start
**Monitoring:** Task completion quality; test coverage

---

### Category 3: Documentation Risks

---

#### R-010: Claude Code Schema Documentation Incomplete

| Attribute | Value |
|-----------|-------|
| **Risk ID** | R-010 |
| **Category** | Documentation |
| **Description** | EN-004 TASK-003 requires documenting Claude Code JSON schema dependency. Schema is not officially published by Anthropic, creating uncertainty about stability and versioning. |
| **Root Cause** | External dependency on undocumented Claude Code internals; no schema version tracking |
| **Likelihood** | 4 - Probable |
| **Consequence** | 2 - Marginal |
| **Risk Score** | **8 (YELLOW)** |
| **Evidence** | XPLAT-001 e-008 RSK-016: "The script parses a specific JSON structure from Claude Code. If Claude Code changes its JSON schema, the script will fail silently (returning defaults). No schema validation exists." |

**Potential Impact:**
- Documentation becomes outdated when Claude Code updates
- Users don't know what Claude Code version is compatible
- Schema changes cause silent failures with no warning
- Support burden for schema-related issues

**Mitigation Strategy:**

1. **Immediate** (Before TASK-003):
   - Document current JSON schema based on test payloads
   - Identify all JSON paths used by statusline.py:
     - model.display_name
     - model.id
     - context_window.context_window_size
     - context_window.current_usage.*
     - cost.total_cost_usd
     - cost.total_duration_ms
     - workspace.current_dir
     - cwd
     - transcript_path

2. **Short-term** (During TASK-003):
   - Add "JSON Schema Dependency" section to documentation
   - Include example JSON payload
   - Document graceful degradation when fields missing
   - Add note about unofficial schema status
   - Recommend users monitor Claude Code release notes

3. **Long-term** (Post-implementation):
   - Consider adding schema version detection if possible
   - Monitor Claude Code updates for schema changes

**Residual Risk After Mitigation:**

| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 3 - Possible | 2 - Marginal | **6 (YELLOW)** |

**Risk Owner:** Documentation Team
**Target Resolution:** TASK-003 completion
**Monitoring:** Claude Code updates; user schema reports

---

#### R-011: WSL vs Native Windows Confusion Persists

| Attribute | Value |
|-----------|-------|
| **Risk ID** | R-011 |
| **Category** | Documentation |
| **Description** | EN-004 TASK-005 adds WSL clarification, but documentation may still not clearly guide users to correct environment. Windows users have 3 distinct environments (native PowerShell, WSL, Git Bash) with different behaviors. |
| **Root Cause** | Windows environment complexity; user knowledge gaps |
| **Likelihood** | 4 - Probable |
| **Consequence** | 3 - Moderate |
| **Risk Score** | **12 (YELLOW)** |
| **Evidence** | XPLAT-001 e-008 RSK-006: "Documentation does not clearly distinguish between native Windows PowerShell, WSL, and Git Bash environments, leading to installation failures and user confusion." |

**Potential Impact:**
- Windows users follow wrong instructions for their environment
- Installation failures due to path handling differences
- Git command availability varies by environment
- Support burden for environment-specific issues
- User frustration and abandonment

**Mitigation Strategy:**

1. **Immediate** (Before TASK-005):
   - Create decision tree for Windows users:
   ```
   Which Windows environment are you using?

   1. Windows Terminal with PowerShell (Native Windows)
      → Use native Windows instructions
      → Paths: C:\Users\...
      → Git for Windows required

   2. WSL (Ubuntu/Debian in Windows)
      → Use Linux instructions
      → Paths: /home/...
      → Git installed via apt

   3. Git Bash (MINGW/MSYS2)
      → Use Git Bash-specific instructions
      → Paths: /c/Users/... (Unix-style)
      → Git included with Git Bash
   ```

2. **Short-term** (During TASK-005):
   - Add environment detection guidance
   - Document differences in GETTING_STARTED.md
   - Include environment-specific screenshots
   - Add "Common Issues" section for Windows

3. **Long-term** (Post-implementation):
   - Monitor Windows user support requests
   - Update documentation based on common issues

**Residual Risk After Mitigation:**

| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 2 - Unlikely | 2 - Marginal | **4 (GREEN)** |

**Risk Owner:** Documentation Team
**Target Resolution:** TASK-005 completion
**Monitoring:** Windows user feedback; support tickets

---

#### R-012: Documentation Review and Quality

| Attribute | Value |
|-----------|-------|
| **Risk ID** | R-012 |
| **Category** | Documentation |
| **Description** | EN-004 adds substantial documentation (7 tasks, 11h effort). Without peer review, documentation may contain errors, unclear instructions, or miss important details. |
| **Root Cause** | Single-author documentation without external review process |
| **Likelihood** | 3 - Possible |
| **Consequence** | 1 - Minimal |
| **Risk Score** | **3 (GREEN)** |
| **Evidence** | No documentation review process defined in FEAT-002 |

**Potential Impact:**
- Typos or technical errors in documentation
- Instructions unclear to new users
- Missing important edge cases or warnings
- Inconsistent formatting or terminology
- User confusion requiring support intervention

**Mitigation Strategy:**

1. **Immediate** (Before EN-004 start):
   - Define documentation review checklist:
     - [ ] Technical accuracy verified
     - [ ] All code examples tested
     - [ ] Platform-specific instructions accurate
     - [ ] Links functional
     - [ ] Formatting consistent
     - [ ] Terminology consistent
     - [ ] No typos or grammatical errors

2. **Short-term** (During EN-004):
   - Self-review using checklist before marking complete
   - Test all documented procedures on fresh systems
   - Verify all code snippets execute correctly

3. **Long-term** (Post-implementation):
   - Consider community feedback mechanism
   - Monitor documentation-related issues

**Residual Risk After Mitigation:**

| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 2 - Unlikely | 1 - Minimal | **2 (GREEN)** |

**Risk Owner:** Documentation Team
**Target Resolution:** Before EN-004 completion
**Monitoring:** User feedback; documentation issue reports

---

## Risk Mitigation Priority Matrix

### Immediate Actions (Before Implementation Start)

| Priority | Risk ID | Action | Effort | Impact |
|----------|---------|--------|--------|--------|
| 1 | R-003 | Create complete emoji inventory | 1h | High |
| 2 | R-006 | Baseline VS Code terminal testing | 1h | High |
| 3 | R-007 | Add locale testing to CI/CD | 0.5h | Medium |
| 4 | R-001 | Design encoding error handling | 0.5h | Medium |
| 5 | R-009 | Create VS Code testing checklist | 0.5h | Medium |

**Total Immediate Effort:** 3.5 hours

### During Implementation

| Priority | Risk ID | Action | Owner | Timeline |
|----------|---------|--------|-------|----------|
| 1 | R-003 | Implement comprehensive emoji fallback | Dev | TASK-003 |
| 2 | R-006 | Execute VS Code compatibility testing | Dev | TASK-004 |
| 3 | R-005 | Add regression test cases | Dev | Throughout EN-003 |
| 4 | R-007 | Execute locale-specific testing | Dev | TASK-001 |
| 5 | R-011 | Create Windows environment decision tree | Doc | TASK-005 |

### Post-Implementation Monitoring

| Risk ID | Monitoring KPI | Threshold | Action |
|---------|---------------|-----------|--------|
| R-001 | Encoding error reports | > 2/month | Review encoding strategy |
| R-002 | HOME-related failures | > 1/month | Enhance error messaging |
| R-006 | VS Code display issues | > 3/month | Add VS Code-specific config |
| R-010 | Schema change reports | Any | Update documentation |
| R-011 | Windows environment confusion | > 5/month | Enhance decision tree |

---

## Residual Risk Summary

### Post-Mitigation Risk Distribution

| Risk Level | Before Mitigation | After Mitigation | Change |
|------------|-------------------|------------------|--------|
| RED (15-25) | 0 | 0 | - |
| YELLOW (6-12) | 7 | 1 | ↓6 |
| GREEN (1-5) | 5 | 11 | ↑6 |

### Remaining YELLOW Risk (Post-Mitigation)

| Risk ID | Description | Residual Score | Rationale |
|---------|-------------|---------------|-----------|
| R-010 | Claude Code schema documentation | 6 (YELLOW) | External dependency; cannot fully control schema stability |

**Recommendation:** Accept residual risk R-010 with active monitoring of Claude Code updates.

---

## Risk-Informed Recommendations

### Priority Ordering Based on Risk

The following implementation order minimizes cumulative risk exposure:

1. **TASK-001 (EN-003): Subprocess encoding** → Mitigates R-001, R-007
   - Add encoding='utf-8', errors='replace'
   - Test with LANG=C locale
   - **Risk Reduction:** 2 YELLOW → GREEN

2. **TASK-003 (EN-003): ASCII emoji fallback** → Mitigates R-003
   - Complete emoji inventory
   - Implement comprehensive fallback
   - **Risk Reduction:** 1 YELLOW → GREEN (highest impact)

3. **TASK-002 (EN-003): Missing HOME handling** → Mitigates R-002, R-008
   - Verify existing handling
   - Add Docker testing
   - **Risk Reduction:** 2 YELLOW → GREEN

4. **TASK-004 (EN-003): VS Code testing** → Mitigates R-006, R-009
   - Execute comprehensive checklist
   - Document results
   - **Risk Reduction:** 2 YELLOW → GREEN

5. **EN-004 Tasks:** → Mitigates R-010, R-011, R-012
   - TASK-005 (WSL clarification) first
   - TASK-003 (Schema docs) with monitoring plan
   - Remaining tasks per planned order

### Critical Success Factors

1. **Comprehensive Testing:** R-005, R-007, R-008 require thorough testing to avoid regressions
2. **VS Code Focus:** R-006 is high-exposure (primary user environment) - deserves extra attention
3. **Emoji Completeness:** R-003 has highest consequence if missed - verify 100% coverage
4. **Documentation Clarity:** R-011 affects significant user base - Windows decision tree critical

### Go/No-Go Criteria for GA Release

**BLOCK GA if:**
- Any YELLOW risk remains unmitigated (except R-010 with documented monitoring)
- VS Code terminal testing (R-006) incomplete
- Emoji fallback (R-003) has known gaps

**ACCEPT for GA if:**
- All YELLOW risks mitigated to GREEN (except R-010)
- All EN-003 tasks complete with test evidence
- All EN-004 documentation tasks complete with review

---

## Risk Monitoring Plan

### Weekly Reviews (During FEAT-002 Implementation)

**Review Checklist:**
- [ ] R-003: Emoji inventory 100% complete?
- [ ] R-006: VS Code testing executed on all 3 platforms?
- [ ] R-007: Locale testing passing in CI/CD?
- [ ] R-005: Regression tests added and passing?
- [ ] R-011: Windows documentation decision tree tested?

### Post-Release Monitoring (First 30 Days)

| Metric | Data Source | Review Frequency |
|--------|-------------|------------------|
| Encoding errors | GitHub Issues, logs | Weekly |
| VS Code display issues | User reports | Weekly |
| Windows environment confusion | Support tickets | Weekly |
| Claude Code schema changes | Anthropic announcements | Daily |
| HOME variable failures | Error logs | Bi-weekly |

### Risk Escalation Triggers

| Trigger | Action | Owner |
|---------|--------|-------|
| > 3 reports of same issue/week | Escalate to project lead | Dev Team |
| Critical bug in GA release | Immediate hotfix planning | Project Lead |
| Claude Code schema change | Emergency documentation update | Doc Team |
| VS Code incompatibility discovered | Issue triage within 24h | Dev Team |

---

## Appendix A: Risk Scoring Reference

### Likelihood Definitions (NPR 7123.1D)

| Score | Level | Description | Probability |
|-------|-------|-------------|-------------|
| 1 | Remote | Very unlikely to occur | < 10% |
| 2 | Unlikely | Not expected but possible | 10-30% |
| 3 | Possible | May occur sometime | 30-50% |
| 4 | Probable | Will probably occur | 50-70% |
| 5 | Near Certain | Expected to occur | > 70% |

### Consequence Definitions (NPR 7123.1D)

| Score | Level | Description |
|-------|-------|-------------|
| 1 | Minimal | Negligible impact; workaround available; cosmetic issue |
| 2 | Marginal | Minor impact; some user inconvenience; reduced functionality |
| 3 | Moderate | Significant impact; feature degradation; affects some users |
| 4 | Significant | Major impact; core functionality affected; affects many users |
| 5 | Catastrophic | Complete failure; data loss; security issue; affects all users |

### Risk Level Thresholds

| Score Range | Level | Color | Action Required |
|-------------|-------|-------|-----------------|
| 1-5 | LOW | GREEN | Accept with monitoring |
| 6-12 | MODERATE | YELLOW | Mitigate before GA release |
| 15-25 | HIGH | RED | Block deployment until resolved |

---

## Appendix B: Traceability Matrix

### Risk to FEAT-002 Task Mapping

| Risk ID | Enabler | Task | Gap ID | RSK (XPLAT-001) |
|---------|---------|------|--------|-----------------|
| R-001 | EN-003 | TASK-001 | G-007 | RSK-026 |
| R-002 | EN-003 | TASK-002 | G-009 | RSK-024 |
| R-003 | EN-003 | TASK-003 | G-014 | RSK-009 |
| R-004 | EN-003 | All | - | RSK-020 |
| R-005 | EN-003 | All | - | - |
| R-006 | EN-003 | TASK-004 | G-008 | RSK-011 |
| R-007 | EN-003 | TASK-001 | G-007 | RSK-026 |
| R-008 | EN-003 | TASK-002 | G-009 | RSK-004 |
| R-009 | EN-003 | TASK-004 | - | - |
| R-010 | EN-004 | TASK-003 | G-013 | RSK-016 |
| R-011 | EN-004 | TASK-005 | - | RSK-006 |
| R-012 | EN-004 | All | - | - |

### Risk to Code Location Mapping

| Risk ID | Code Location | Function/Section |
|---------|---------------|------------------|
| R-001 | Lines 606-612, 624-629 | get_git_info() subprocess calls |
| R-002 | Lines 161-169, 242-252 | _get_config_paths(), _resolve_state_path() |
| R-003 | Lines 724-733, 749-897 | All segment building functions |
| R-006 | - | VS Code terminal (external) |

---

## Appendix C: Emoji Inventory (Complete)

### All Unicode Characters Requiring ASCII Fallback

| Category | Unicode | Character | use_emoji=true | use_emoji=false | Location |
|----------|---------|-----------|----------------|-----------------|----------|
| Model Opus | U+1F535 | 🔵 | 🔵 Opus 4.6 | [O] Opus 4.6 | Line 724 |
| Model Sonnet | U+1F7E3 | 🟣 | 🟣 Sonnet 4.5 | [S] Sonnet 4.5 | Line 724 |
| Model Haiku | U+1F7E2 | 🟢 | 🟢 Haiku 3.7 | [H] Haiku 3.7 | Line 724 |
| Model Unknown | U+26AA | ⚪ | ⚪ Unknown | [?] Unknown | Line 725 |
| Context | U+1F4CA | 📊 | 📊 | CTX | Line 749 |
| Cost | U+1F4B0 | 💰 | 💰 | $ | Line 768 |
| Tokens | U+26A1 | ⚡ | ⚡ | ! | Line 784 |
| Tokens Fresh | U+2192 | → | → | -> | Line 792 |
| Tokens Cached | U+21BA | ↺ | ↺ | @ | Line 792 |
| Session | U+23F1 | ⏱️ | ⏱️ | [T] | Line 803 |
| Compaction | U+1F4C9 | 📉 | 📉 | [v] | Line 827 |
| Tools | U+1F527 | 🔧 | 🔧 | [W] | Line 848 |
| Git | U+1F33F | 🌿 | 🌿 | [G] | Line 869 |
| Directory | U+1F4C2 | 📂 | 📂 | [D] | Line 893 |
| Progress Filled | U+2593 | ▓ | ▓ | # | Line 650 |
| Progress Empty | U+2591 | ░ | ░ | - | Line 650 |
| Git Clean | U+2713 | ✓ | ✓ | + | Line 872 |
| Git Dirty | U+25CF | ● | ● | * | Line 876 |

**Total Unicode Characters:** 18
**Implementation Strategy:** Create `EMOJI_SYMBOLS` and `ASCII_SYMBOLS` dictionaries with `get_symbol(name, config)` lookup function.

---

## Appendix D: Testing Checklist

### EN-003 TASK-001: Subprocess Encoding

- [ ] Add `encoding='utf-8', errors='replace'` to git subprocess calls
- [ ] Test on system with LANG=C locale
- [ ] Test on system with LANG=POSIX locale
- [ ] Test on Windows with non-Unicode codepage
- [ ] Test with git branch name containing non-ASCII characters
- [ ] Verify CI/CD passes with locale test
- [ ] Verify debug logging on encoding errors

### EN-003 TASK-002: Missing HOME Variable

- [ ] Verify existing code handles missing HOME (lines 161-169, 242-252)
- [ ] Test in Docker container with `unset HOME`
- [ ] Test with HOME pointing to non-existent directory
- [ ] Test with HOME pointing to read-only directory (/
- [ ] Test with HOME set to empty string
- [ ] Verify state file operations gracefully degrade
- [ ] Verify config loading gracefully degrades
- [ ] Verify debug logging when HOME unavailable

### EN-003 TASK-003: ASCII Emoji Fallback

- [ ] Create complete emoji inventory (18 characters)
- [ ] Implement `get_symbol(name, config)` function
- [ ] Create `EMOJI_SYMBOLS` dictionary (18 entries)
- [ ] Create `ASCII_SYMBOLS` dictionary (18 entries)
- [ ] Replace all hardcoded emoji with `get_symbol()` calls
- [ ] Test output with `use_emoji=true` (verify all emoji appear)
- [ ] Test output with `use_emoji=false` (verify no Unicode > U+007F)
- [ ] Test on Windows cmd.exe with ASCII mode
- [ ] Test on terminal with TERM=dumb
- [ ] Add automated test case for ASCII mode
- [ ] Visual inspection of all segments in ASCII mode

### EN-003 TASK-004: VS Code Terminal Testing

- [ ] Test on macOS VS Code with default terminal
- [ ] Test on Linux (Ubuntu) VS Code with default terminal
- [ ] Test on Windows VS Code with PowerShell
- [ ] Test on Windows VS Code with Git Bash
- [ ] Test with `use_emoji=true` in all environments
- [ ] Test with `use_emoji=false` in all environments
- [ ] Test progress bar rendering in all environments
- [ ] Test ANSI 256-color support in all environments
- [ ] Test with VS Code dark theme
- [ ] Test with VS Code light theme
- [ ] Test with different terminal fonts (Monospace, Consolas, Fira Code)
- [ ] Document recommended VS Code settings (if needed)
- [ ] Capture screenshots for documentation

---

*This risk assessment was generated by nse-risk agent (v2.1.0). Human review recommended.*
