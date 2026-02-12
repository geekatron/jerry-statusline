# Cross-Platform Risk Register for jerry-statusline

**PS ID:** XPLAT-001
**Entry ID:** e-008
**Topic:** Cross-Platform Risk Register
**Date:** 2026-02-03
**Author:** nse-risk v1.0.0

---

```
DISCLAIMER: This guidance is AI-generated based on NASA Systems Engineering
standards. It is advisory only and does not constitute official NASA guidance.
```

---

## Executive Summary

This risk register documents identified risks for cross-platform deployment of jerry-statusline (ECW Status Line v2.1.0) based on comprehensive gap analysis (e-003) and adversarial critique (e-006). The assessment uses NASA NPR 8000.4C 5x5 risk matrix methodology.

### Overall Risk Profile

| Category | Critical (Red) | High (Yellow) | Medium (Green) | Total |
|----------|----------------|---------------|----------------|-------|
| Platform Compatibility | 2 | 3 | 2 | 7 |
| Terminal Display | 1 | 2 | 2 | 5 |
| Dependency | 1 | 2 | 1 | 4 |
| User Experience | 0 | 3 | 2 | 5 |
| Operational | 1 | 2 | 2 | 5 |
| **Total** | **5** | **12** | **9** | **26** |

### Risk Heat Map (5x5 Matrix)

```
CONSEQUENCE
     |  1-Minimal  2-Marginal  3-Moderate  4-Significant  5-Catastrophic
-----+--------------------------------------------------------------------
  5  |     5          10          15           20             25
Near |   (Green)    (Yellow)     (Red)        (Red)          (Red)
Cert |              RSK-012     RSK-001      RSK-003
     |                          RSK-007      RSK-009
-----+--------------------------------------------------------------------
  4  |     4           8          12           16             20
Prob |   (Green)    (Yellow)    (Yellow)      (Red)          (Red)
     |   RSK-026    RSK-014     RSK-002      RSK-004
     |              RSK-022     RSK-008      RSK-005
     |                          RSK-015      RSK-006
-----+--------------------------------------------------------------------
  3  |     3           6           9           12             15
Poss |   (Green)    (Yellow)    (Yellow)    (Yellow)         (Red)
     |              RSK-017     RSK-010      RSK-011         RSK-021
     |              RSK-018     RSK-016      RSK-013
     |              RSK-019     RSK-023      RSK-020
-----+--------------------------------------------------------------------
  2  |     2           4           6            8             10
Unlik|   (Green)    (Green)     (Yellow)    (Yellow)       (Yellow)
     |              RSK-024     RSK-025
-----+--------------------------------------------------------------------
  1  |     1           2           3            4              5
Remot|   (Green)    (Green)     (Green)      (Green)        (Green)
     |
-----+--------------------------------------------------------------------
LIKELIHOOD
```

**Legend:**
- Green (1-5): Accept risk with monitoring
- Yellow (6-12): Mitigate risk before GA
- Red (15-25): Critical - Block deployment until resolved

---

## Risk Categories

### Category 1: Platform Compatibility Risks

---

#### RSK-XPLAT-001: Windows Native Support Untested

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-XPLAT-001 |
| **Category** | Platform Compatibility |
| **Description** | Zero actual test execution has occurred on Windows 10/11 native environments. All Windows compatibility claims are assumption-based from code inspection only. |
| **Root Cause** | Development performed exclusively on macOS; no CI/CD pipeline with Windows runners |
| **Likelihood** | 5 - Near Certain (defects exist) |
| **Consequence** | 3 - Moderate (feature degradation, user confusion) |
| **Risk Score** | **15 (RED)** |
| **Evidence** | e-006 Section 2.2: "ZERO Windows tests have been executed"; e-004: PCT-006, PHT-003 all "Pending" |

**Potential Impact:**
- Path handling failures with `C:\Users\...` format
- ANSI color rendering issues in PowerShell/cmd.exe
- Git subprocess calls may fail with non-standard PATH
- State file location resolution errors
- Silent failures with no user feedback

**Mitigation Strategy:**
1. **Immediate**: Execute manual testing on Windows 10 and Windows 11
2. **Short-term**: Implement GitHub Actions CI/CD with `windows-latest` runner
3. **Long-term**: Add Windows-specific test payloads with `C:\Users\...` paths

**Residual Risk After Mitigation:**
| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 2 - Unlikely | 2 - Marginal | **4 (GREEN)** |

**Risk Owner:** Development Team
**Target Resolution:** Before GA release
**Monitoring:** CI/CD test results on each commit

---

#### RSK-XPLAT-002: Linux Testing Not Performed

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-XPLAT-002 |
| **Category** | Platform Compatibility |
| **Description** | Linux compatibility is assumed but never verified on actual Linux systems. Tests use Unix-style paths but run on macOS developer machine. |
| **Root Cause** | Development focus on macOS; no Linux CI/CD runners configured |
| **Likelihood** | 4 - Probable |
| **Consequence** | 3 - Moderate |
| **Risk Score** | **12 (YELLOW)** |
| **Evidence** | e-003 Section 2.1: "Tests only run locally on developer machine"; e-006: "No evidence of Ubuntu/Debian/RHEL testing" |

**Potential Impact:**
- Distribution-specific Python path differences (`python` vs `python3`)
- Package manager variations affecting prerequisites
- Terminal emulator compatibility differences
- TERM environment variable handling

**Mitigation Strategy:**
1. **Immediate**: Execute manual testing on Ubuntu 22.04 LTS
2. **Short-term**: Add `ubuntu-latest` to GitHub Actions matrix
3. **Long-term**: Test on Fedora, Arch Linux for broader coverage

**Residual Risk After Mitigation:**
| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 2 - Unlikely | 2 - Marginal | **4 (GREEN)** |

**Risk Owner:** Development Team
**Target Resolution:** Before GA release
**Monitoring:** CI/CD test results; user issue reports

---

#### RSK-XPLAT-003: Alpine Linux / musl libc Incompatibility

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-XPLAT-003 |
| **Category** | Platform Compatibility |
| **Description** | Requirements specify "glibc 2.17+" but Alpine Linux uses musl libc. Alpine is the default Docker base image, making this a critical gap for containerized deployments. |
| **Root Cause** | Requirements document (e-002) explicitly excludes Alpine without documentation; container scenarios not considered |
| **Likelihood** | 5 - Near Certain (users will try Docker) |
| **Consequence** | 4 - Significant (complete failure in common environment) |
| **Risk Score** | **20 (RED)** |
| **Evidence** | e-006 Section 1.1: "Alpine Linux is the default base image for Docker containers... explicitly excludes Alpine Linux, yet Alpine is never mentioned as unsupported" |

**Potential Impact:**
- `os.path.expanduser()` edge case differences with musl
- Subprocess timeout handling variations
- Unicode locale handling differences
- Complete feature failure in Docker environments
- User confusion due to undocumented limitation

**Mitigation Strategy:**
1. **Immediate**: Test on `python:3.11-alpine` Docker image
2. **Short-term**: Either fix compatibility issues OR explicitly document Alpine as unsupported
3. **Long-term**: Add container testing to CI/CD pipeline

**Residual Risk After Mitigation:**
| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 2 - Unlikely | 2 - Marginal | **4 (GREEN)** |

**Risk Owner:** Development Team
**Target Resolution:** Before GA release
**Monitoring:** Docker Hub image testing; container deployment reports

---

#### RSK-XPLAT-004: Docker Container Environment Failures

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-XPLAT-004 |
| **Category** | Platform Compatibility |
| **Description** | Docker containers typically lack TTY, causing `os.get_terminal_size()` to always fail. Git may not be installed. HOME environment may not be set. |
| **Root Cause** | Container scenarios completely absent from analysis (e-001 through e-005) |
| **Likelihood** | 4 - Probable |
| **Consequence** | 4 - Significant |
| **Risk Score** | **16 (RED)** |
| **Evidence** | e-006 Section 1.2: "Docker containers: No TTY, os.get_terminal_size() always fails, git may not be installed" |

**Potential Impact:**
- Terminal width detection returns default 120, may cause display issues
- Git segment silently disabled without explanation
- State file operations may fail if HOME not set
- No graceful degradation messaging

**Mitigation Strategy:**
1. **Immediate**: Test in Docker container without TTY (`docker run -t=false`)
2. **Short-term**: Add explicit container detection and graceful degradation
3. **Long-term**: Document container deployment requirements and limitations

**Residual Risk After Mitigation:**
| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 2 - Unlikely | 3 - Moderate | **6 (YELLOW)** |

**Risk Owner:** Development Team
**Target Resolution:** Before GA release
**Monitoring:** Container deployment feedback; issue tracker

---

#### RSK-XPLAT-005: ARM Architecture Untested

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-XPLAT-005 |
| **Category** | Platform Compatibility |
| **Description** | ARM Linux (Raspberry Pi) and Windows on ARM (Snapdragon) are growing developer platforms with no testing coverage. |
| **Root Cause** | Focus on x86_64 architecture; ARM not considered in scope |
| **Likelihood** | 4 - Probable (ARM adoption increasing) |
| **Consequence** | 4 - Significant |
| **Risk Score** | **16 (RED)** |
| **Evidence** | e-006 Section 1.1: "ARM Linux (Raspberry Pi): Growing developer platform. No architecture-specific testing." |

**Potential Impact:**
- Python behavior differences on ARM
- Subprocess execution variations
- Performance characteristics unknown
- Apple Silicon (M1/M2/M3) compatibility assumed but not verified

**Mitigation Strategy:**
1. **Immediate**: Verify Apple Silicon compatibility (M1/M2/M3 Macs)
2. **Short-term**: Test on Raspberry Pi 4 with Raspberry Pi OS
3. **Long-term**: Consider ARM runners in CI/CD if adoption increases

**Residual Risk After Mitigation:**
| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 2 - Unlikely | 3 - Moderate | **6 (YELLOW)** |

**Risk Owner:** Development Team
**Target Resolution:** Post-GA (lower priority)
**Monitoring:** User issue reports from ARM users

---

#### RSK-XPLAT-006: WSL vs Native Windows Confusion

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-XPLAT-006 |
| **Category** | Platform Compatibility |
| **Description** | Documentation does not clearly distinguish between native Windows PowerShell, WSL, and Git Bash environments, leading to installation failures and user confusion. |
| **Root Cause** | Documentation gap; Windows environment complexity underestimated |
| **Likelihood** | 4 - Probable |
| **Consequence** | 4 - Significant |
| **Risk Score** | **16 (RED)** |
| **Evidence** | e-003 Section 3.2: "Documentation mentions Windows but doesn't distinguish: Native Windows PowerShell, WSL, Git Bash/MSYS2" |

**Potential Impact:**
- Users follow wrong instructions for their environment
- Path handling differences cause failures
- Git command availability varies by environment
- Inconsistent terminal capability expectations

**Mitigation Strategy:**
1. **Immediate**: Add environment clarification section to GETTING_STARTED.md
2. **Short-term**: Create decision tree for Windows users
3. **Long-term**: Test and document all three Windows environments

**Residual Risk After Mitigation:**
| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 2 - Unlikely | 2 - Marginal | **4 (GREEN)** |

**Risk Owner:** Documentation Team
**Target Resolution:** Before GA release
**Monitoring:** User support requests; documentation feedback

---

#### RSK-XPLAT-007: CI/CD Pipeline Not Implemented

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-XPLAT-007 |
| **Category** | Platform Compatibility |
| **Description** | Despite comprehensive CI/CD workflow documentation in e-004, no actual GitHub Actions workflow exists. All verification is theoretical. |
| **Root Cause** | Documentation theater; procedures documented but not executed |
| **Likelihood** | 5 - Near Certain (no automation exists) |
| **Consequence** | 3 - Moderate |
| **Risk Score** | **15 (RED)** |
| **Evidence** | e-006 Section 5.4: "No `.github/workflows/` directory; No CI/CD actually running" |

**Potential Impact:**
- Platform-specific bugs go undetected until user reports
- Regression risk on each code change
- No automated quality gate before releases
- Manual testing burden on maintainers

**Mitigation Strategy:**
1. **Immediate**: Create `.github/workflows/test.yml` from e-004 specification
2. **Short-term**: Enable required status checks on main branch
3. **Long-term**: Add code coverage requirements

**Residual Risk After Mitigation:**
| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 1 - Remote | 2 - Marginal | **2 (GREEN)** |

**Risk Owner:** DevOps Team
**Target Resolution:** Before GA release
**Monitoring:** CI/CD run history; test pass rates

---

### Category 2: Terminal Display Risks

---

#### RSK-XPLAT-008: ANSI Color Support Varies Across Terminals

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-XPLAT-008 |
| **Category** | Terminal Display |
| **Description** | ANSI 256-color escape sequences may not render correctly on legacy Windows terminals (cmd.exe, older PowerShell) or non-standard terminal emulators. |
| **Root Cause** | No terminal capability detection; assumes universal ANSI support |
| **Likelihood** | 4 - Probable |
| **Consequence** | 3 - Moderate |
| **Risk Score** | **12 (YELLOW)** |
| **Evidence** | e-003 Section 1.5: "Windows cmd.exe: Limited - may not support ANSI"; e-006 Section 2.4: "Windows conhost: Works - Limited without VT mode" |

**Potential Impact:**
- Garbled output with raw escape codes visible
- Color codes appear as `[38;5;82m` text
- Status line unusable on legacy terminals
- User perception of broken software

**Mitigation Strategy:**
1. **Immediate**: Document Windows Terminal as recommended terminal
2. **Short-term**: Add config option `"colors": {"enabled": false}` for fallback
3. **Long-term**: Consider NO_COLOR environment variable support (https://no-color.org/)

**Residual Risk After Mitigation:**
| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 2 - Unlikely | 2 - Marginal | **4 (GREEN)** |

**Risk Owner:** Development Team
**Target Resolution:** Before GA release
**Monitoring:** User reports of display issues

---

#### RSK-XPLAT-009: Emoji Rendering Inconsistent

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-XPLAT-009 |
| **Category** | Terminal Display |
| **Description** | Emoji characters used for model indicators, progress bars, and icons may render as mojibake, placeholder boxes, or incorrect widths on terminals without proper font support. |
| **Root Cause** | Emoji assumed to work; no fallback mechanism for unsupported terminals |
| **Likelihood** | 5 - Near Certain |
| **Consequence** | 4 - Significant |
| **Risk Score** | **20 (RED)** |
| **Evidence** | e-006 Section 7 (e-001 critique): "Claims emoji is 'configurable' but doesn't analyze what happens when emoji is enabled on terminals that don't support it (mojibake)" |

**Potential Impact:**
- Model icons appear as `????` or boxes
- Progress bar characters misaligned
- Status line becomes unreadable
- Terminal width calculations incorrect due to emoji width

**Mitigation Strategy:**
1. **Immediate**: Ensure `"use_emoji": false` config option fully functional
2. **Short-term**: Provide ASCII-only alternative for all emoji (e.g., `[O]` for Opus)
3. **Long-term**: Auto-detect emoji support if possible

**Residual Risk After Mitigation:**
| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 2 - Unlikely | 2 - Marginal | **4 (GREEN)** |

**Risk Owner:** Development Team
**Target Resolution:** Before GA release
**Monitoring:** User configuration feedback

---

#### RSK-XPLAT-010: Terminal Width Detection Unreliable

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-XPLAT-010 |
| **Category** | Terminal Display |
| **Description** | `os.get_terminal_size()` fails in non-TTY environments (Docker, pipes, SSH edge cases), returning default width 120 which may not match actual display. |
| **Root Cause** | Code handles OSError but silently uses potentially incorrect default |
| **Likelihood** | 3 - Possible |
| **Consequence** | 3 - Moderate |
| **Risk Score** | **9 (YELLOW)** |
| **Evidence** | Code line 264-266: `try: return os.get_terminal_size().columns except OSError: return 120` |

**Potential Impact:**
- Status line may be too long for actual terminal
- Auto-compact mode may not trigger when needed
- Truncation at wrong positions
- Display wrapping issues

**Mitigation Strategy:**
1. **Immediate**: Document terminal width requirements
2. **Short-term**: Add COLUMNS environment variable fallback
3. **Long-term**: Consider configurable width override option

**Residual Risk After Mitigation:**
| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 2 - Unlikely | 2 - Marginal | **4 (GREEN)** |

**Risk Owner:** Development Team
**Target Resolution:** Post-GA (lower priority)
**Monitoring:** Display issue reports

---

#### RSK-XPLAT-011: VS Code Terminal ANSI Limitations

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-XPLAT-011 |
| **Category** | Terminal Display |
| **Description** | VS Code integrated terminal has known 256-color rendering issues. Since Claude Code users likely use VS Code, this is a high-exposure environment. |
| **Root Cause** | VS Code terminal not tested despite being primary target environment |
| **Likelihood** | 3 - Possible |
| **Consequence** | 4 - Significant |
| **Risk Score** | **12 (YELLOW)** |
| **Evidence** | e-006 Section 1.2: "VS Code integrated terminal: Different ANSI handling than native terminal" |

**Potential Impact:**
- Colors appear different than intended
- Some escape sequences not recognized
- User confusion about "correct" appearance
- Reduced visual utility of status line

**Mitigation Strategy:**
1. **Immediate**: Test in VS Code integrated terminal on all platforms
2. **Short-term**: Document VS Code terminal configuration for optimal display
3. **Long-term**: Consider VS Code-specific color palette if needed

**Residual Risk After Mitigation:**
| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 2 - Unlikely | 3 - Moderate | **6 (YELLOW)** |

**Risk Owner:** Development Team
**Target Resolution:** Before GA release
**Monitoring:** VS Code user feedback

---

#### RSK-XPLAT-012: NO_COLOR Standard Not Respected

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-XPLAT-012 |
| **Category** | Terminal Display |
| **Description** | The NO_COLOR environment variable (https://no-color.org/) is a growing standard for disabling color output. The script does not check for this variable. |
| **Root Cause** | NO_COLOR standard not considered during development |
| **Likelihood** | 5 - Near Certain (standard exists) |
| **Consequence** | 2 - Marginal |
| **Risk Score** | **10 (YELLOW)** |
| **Evidence** | e-006 Section 4.2: "The code does NOT respect the NO_COLOR environment variable" |

**Potential Impact:**
- Users with NO_COLOR set still see colors
- Violates user accessibility preferences
- Script output not compliant with emerging standard
- Potential issues with automated tooling expecting no color

**Mitigation Strategy:**
1. **Immediate**: Check for NO_COLOR at startup, disable colors if set
2. **Short-term**: Document NO_COLOR support
3. **Long-term**: Consider FORCE_COLOR support as well

**Residual Risk After Mitigation:**
| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 1 - Remote | 1 - Minimal | **1 (GREEN)** |

**Risk Owner:** Development Team
**Target Resolution:** Before GA release
**Monitoring:** Standards compliance audits

---

### Category 3: Dependency Risks

---

#### RSK-XPLAT-013: Git Not Available on Windows

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-XPLAT-013 |
| **Category** | Dependency |
| **Description** | Windows does not include Git by default. Git for Windows may not add itself to PATH during installation, causing git commands to fail silently. |
| **Root Cause** | Windows differs from macOS/Linux in not having git pre-installed; PATH configuration varies |
| **Likelihood** | 3 - Possible |
| **Consequence** | 4 - Significant |
| **Risk Score** | **12 (YELLOW)** |
| **Evidence** | e-003 Section 4.2: "Windows Git for Windows may not be in PATH by default" |

**Potential Impact:**
- Git segment silently disappears (design choice)
- User doesn't know if feature is disabled or broken
- No guidance on how to resolve
- Reduced functionality without explanation

**Mitigation Strategy:**
1. **Immediate**: Document Git PATH requirements for Windows
2. **Short-term**: Add debug message when git not found (ECW_DEBUG mode)
3. **Long-term**: Consider optional user notification for missing git

**Residual Risk After Mitigation:**
| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 2 - Unlikely | 2 - Marginal | **4 (GREEN)** |

**Risk Owner:** Documentation Team
**Target Resolution:** Before GA release
**Monitoring:** User support requests about git segment

---

#### RSK-XPLAT-014: Python Version Differences

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-XPLAT-014 |
| **Category** | Dependency |
| **Description** | Python 3.9+ is required but Linux distributions may have older default Python, or use `python` vs `python3` naming inconsistently. |
| **Root Cause** | Linux distribution variation; no version validation at startup |
| **Likelihood** | 4 - Probable |
| **Consequence** | 2 - Marginal |
| **Risk Score** | **8 (YELLOW)** |
| **Evidence** | e-003 Section 4.1: "Linux may have python vs python3 naming inconsistency" |

**Potential Impact:**
- Script fails with syntax errors on Python 3.8 or below
- User confusion about which Python to use
- Different behavior on different Python versions

**Mitigation Strategy:**
1. **Immediate**: Document that `python3` command is required
2. **Short-term**: Add version check at script startup with clear error
3. **Long-term**: Test on Python 3.9, 3.10, 3.11, 3.12 in CI/CD

**Residual Risk After Mitigation:**
| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 1 - Remote | 2 - Marginal | **2 (GREEN)** |

**Risk Owner:** Development Team
**Target Resolution:** Before GA release
**Monitoring:** CI/CD Python version matrix

---

#### RSK-XPLAT-015: Future Python stdlib Changes

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-XPLAT-015 |
| **Category** | Dependency |
| **Description** | The script uses `from __future__ import annotations` which has uncertain future behavior (PEP 563 vs PEP 649). Other stdlib APIs may change in Python 3.13+. |
| **Root Cause** | Technical debt from using features with uncertain long-term stability |
| **Likelihood** | 4 - Probable |
| **Consequence** | 3 - Moderate |
| **Risk Score** | **12 (YELLOW)** |
| **Evidence** | e-006 Section 4.1: "from __future__ import annotations was intended for PEP 563. PEP 649 may change this behavior in Python 3.14+" |

**Potential Impact:**
- Code may require changes for Python 3.14+
- Typing behavior differences
- Potential deprecation warnings in future versions

**Mitigation Strategy:**
1. **Immediate**: Document Python version compatibility policy
2. **Short-term**: Monitor Python development for PEP 649 timeline
3. **Long-term**: Update annotations approach when Python 3.14 releases

**Residual Risk After Mitigation:**
| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 2 - Unlikely | 2 - Marginal | **4 (GREEN)** |

**Risk Owner:** Development Team
**Target Resolution:** Monitor ongoing
**Monitoring:** Python release notes; community discussion

---

#### RSK-XPLAT-016: Claude Code JSON Schema Changes

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-XPLAT-016 |
| **Category** | Dependency |
| **Description** | The script parses a specific JSON structure from Claude Code. If Claude Code changes its JSON schema, the script will fail silently (returning defaults). |
| **Root Cause** | No schema validation; no version compatibility checking |
| **Likelihood** | 3 - Possible |
| **Consequence** | 3 - Moderate |
| **Risk Score** | **9 (YELLOW)** |
| **Evidence** | e-006 Section 4.3: "No schema validation exists. No version compatibility checking." |

**Potential Impact:**
- Segments show wrong or missing data
- Subtle bugs difficult to diagnose
- User sees stale/incorrect information
- No warning when schema changes

**Mitigation Strategy:**
1. **Immediate**: Document known Claude Code JSON schema
2. **Short-term**: Add optional schema version checking
3. **Long-term**: Monitor Claude Code updates for schema changes

**Residual Risk After Mitigation:**
| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 2 - Unlikely | 2 - Marginal | **4 (GREEN)** |

**Risk Owner:** Development Team
**Target Resolution:** Post-GA (monitor)
**Monitoring:** Claude Code release notes; user reports

---

### Category 4: User Experience Risks

---

#### RSK-XPLAT-017: Silent Failures on Edge Cases

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-XPLAT-017 |
| **Category** | User Experience |
| **Description** | The script silently handles errors with debug logging only. Users have no indication when features fail (git segment disappears, state file not saved, etc.). |
| **Root Cause** | Design decision for "clean output" over user feedback; debug mode not discoverable |
| **Likelihood** | 3 - Possible |
| **Consequence** | 2 - Marginal |
| **Risk Score** | **6 (YELLOW)** |
| **Evidence** | e-003 Section 1.4: "Error handling silently hides git segment when git is not found. No user feedback about why git segment is missing." |

**Potential Impact:**
- Users think features are disabled, not broken
- Difficult to troubleshoot issues
- Support burden increases
- Users may abandon tool due to perceived bugs

**Mitigation Strategy:**
1. **Immediate**: Document ECW_DEBUG=1 environment variable
2. **Short-term**: Add startup validation messages in debug mode
3. **Long-term**: Consider optional "verbose" mode for first-run diagnostics

**Residual Risk After Mitigation:**
| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 2 - Unlikely | 2 - Marginal | **4 (GREEN)** |

**Risk Owner:** Development Team
**Target Resolution:** Before GA release
**Monitoring:** Support request analysis

---

#### RSK-XPLAT-018: Confusing Error Messages

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-XPLAT-018 |
| **Category** | User Experience |
| **Description** | When errors occur, messages like "ECW: Parse error" or "ECW: Error - KeyError" provide no actionable guidance for users. |
| **Root Cause** | Error handling designed for robustness, not user-friendliness |
| **Likelihood** | 3 - Possible |
| **Consequence** | 2 - Marginal |
| **Risk Score** | **6 (YELLOW)** |
| **Evidence** | Code lines 932-941: Generic error output without context |

**Potential Impact:**
- Users cannot self-diagnose issues
- Support burden for trivial problems
- Perception of poor software quality

**Mitigation Strategy:**
1. **Immediate**: Improve error message text with suggestions
2. **Short-term**: Add troubleshooting section to documentation
3. **Long-term**: Link to documentation in error output

**Residual Risk After Mitigation:**
| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 2 - Unlikely | 1 - Minimal | **2 (GREEN)** |

**Risk Owner:** Development Team
**Target Resolution:** Before GA release
**Monitoring:** Support request content analysis

---

#### RSK-XPLAT-019: Linux Documentation Missing

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-XPLAT-019 |
| **Category** | User Experience |
| **Description** | GETTING_STARTED.md has comprehensive macOS and Windows sections but NO Linux installation guidance. Linux users have no documentation. |
| **Root Cause** | Development focus on macOS; Linux assumed to be "obvious" |
| **Likelihood** | 3 - Possible |
| **Consequence** | 2 - Marginal |
| **Risk Score** | **6 (YELLOW)** |
| **Evidence** | e-003 Section 3.1: "Linux installation: NOT PRESENT" |

**Potential Impact:**
- Linux users cannot install without guessing
- Excludes significant developer population
- Community perception of incomplete project

**Mitigation Strategy:**
1. **Immediate**: Add Linux section to GETTING_STARTED.md
2. **Short-term**: Cover apt, dnf, pacman package managers
3. **Long-term**: Add distribution-specific notes (Ubuntu, Fedora, Arch)

**Residual Risk After Mitigation:**
| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 1 - Remote | 1 - Minimal | **1 (GREEN)** |

**Risk Owner:** Documentation Team
**Target Resolution:** Before GA release
**Monitoring:** Documentation coverage audits

---

#### RSK-XPLAT-020: No Upgrade Path Documentation

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-XPLAT-020 |
| **Category** | User Experience |
| **Description** | No documentation exists for upgrading from v2.0.0 to v2.1.0. Config file format changes, state file migration, and breaking changes are not documented. |
| **Root Cause** | Version management not prioritized in early development |
| **Likelihood** | 3 - Possible |
| **Consequence** | 4 - Significant |
| **Risk Score** | **12 (YELLOW)** |
| **Evidence** | e-006 Section 6.3: "No changelog for v2.0.0 -> v2.1.0; No migration guide; Breaking changes not identified" |

**Potential Impact:**
- Existing users have broken configurations after upgrade
- State file format incompatibility
- Lost user customizations
- Negative user experience during upgrade

**Mitigation Strategy:**
1. **Immediate**: Document v2.0.0 -> v2.1.0 changes
2. **Short-term**: Add CHANGELOG.md with migration notes
3. **Long-term**: Implement config version checking with auto-migration

**Residual Risk After Mitigation:**
| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 2 - Unlikely | 2 - Marginal | **4 (GREEN)** |

**Risk Owner:** Documentation Team
**Target Resolution:** Before GA release
**Monitoring:** Upgrade-related support requests

---

#### RSK-XPLAT-021: No Uninstall Documentation

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-XPLAT-021 |
| **Category** | User Experience |
| **Description** | No uninstall instructions exist. State file, config file, and settings.json modification are left behind when users want to remove the tool. |
| **Root Cause** | Uninstall scenario not considered |
| **Likelihood** | 3 - Possible |
| **Consequence** | 5 - Catastrophic (data hygiene concern) |
| **Risk Score** | **15 (RED)** |
| **Evidence** | e-006 Section 6.1: "No uninstall instructions; State file left behind" |

**Potential Impact:**
- Orphaned files in user home directory
- Settings.json modification persists
- User cannot cleanly remove tool
- Security concern for abandoned state files

**Mitigation Strategy:**
1. **Immediate**: Add uninstall section to documentation
2. **Short-term**: List all files created by the tool
3. **Long-term**: Consider uninstall script

**Residual Risk After Mitigation:**
| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 1 - Remote | 2 - Marginal | **2 (GREEN)** |

**Risk Owner:** Documentation Team
**Target Resolution:** Before GA release
**Monitoring:** User cleanup requests

---

### Category 5: Operational Risks

---

#### RSK-XPLAT-022: State File Corruption

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-XPLAT-022 |
| **Category** | Operational |
| **Description** | State file (`~/.claude/ecw-statusline-state.json`) could become corrupted due to partial writes, concurrent access, or disk failures. Corruption handling is minimal. |
| **Root Cause** | No atomic write operations; no backup/recovery mechanism |
| **Likelihood** | 4 - Probable |
| **Consequence** | 2 - Marginal |
| **Risk Score** | **8 (YELLOW)** |
| **Evidence** | Code lines 236-241: Direct file write without atomic operation |

**Potential Impact:**
- Compaction detection stops working
- JSON parse errors on startup
- User must manually delete state file
- Loss of session continuity tracking

**Mitigation Strategy:**
1. **Immediate**: Document state file recovery (delete to reset)
2. **Short-term**: Add graceful handling of corrupted state (reset to defaults)
3. **Long-term**: Implement atomic write (write to temp, then rename)

**Residual Risk After Mitigation:**
| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 2 - Unlikely | 1 - Minimal | **2 (GREEN)** |

**Risk Owner:** Development Team
**Target Resolution:** Post-GA (low impact)
**Monitoring:** User reports of parse errors

---

#### RSK-XPLAT-023: Config File Permission Issues

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-XPLAT-023 |
| **Category** | Operational |
| **Description** | Config file may have restrictive permissions preventing read access, or user may not have write permission for state file directory. |
| **Root Cause** | No permission checking; silent failure on permission errors |
| **Likelihood** | 3 - Possible |
| **Consequence** | 3 - Moderate |
| **Risk Score** | **9 (YELLOW)** |
| **Evidence** | Code line 181: IOError caught but only logged to debug |

**Potential Impact:**
- Config customizations not applied
- State file not saved (compaction tracking fails)
- User confusion about why settings don't work

**Mitigation Strategy:**
1. **Immediate**: Document required file permissions
2. **Short-term**: Add permission check with descriptive error
3. **Long-term**: Consider fallback locations for state file

**Residual Risk After Mitigation:**
| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 2 - Unlikely | 2 - Marginal | **4 (GREEN)** |

**Risk Owner:** Development Team
**Target Resolution:** Before GA release
**Monitoring:** Permission-related error reports

---

#### RSK-XPLAT-024: Read-Only Filesystem Scenarios

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-XPLAT-024 |
| **Category** | Operational |
| **Description** | In read-only filesystem scenarios (containers, restricted environments), state file write silently fails. Compaction detection becomes non-functional without user awareness. |
| **Root Cause** | Silent failure design; no alternative for read-only environments |
| **Likelihood** | 2 - Unlikely |
| **Consequence** | 3 - Moderate |
| **Risk Score** | **6 (YELLOW)** |
| **Evidence** | e-006 Section 3.1: "This silently fails on read-only filesystems. But the compaction detection feature DEPENDS on this state." |

**Potential Impact:**
- Compaction indicator never appears
- User doesn't know feature is non-functional
- No warning or documentation of limitation

**Mitigation Strategy:**
1. **Immediate**: Document read-only filesystem limitation
2. **Short-term**: Add one-time warning when state file cannot be written
3. **Long-term**: Consider in-memory state option for read-only environments

**Residual Risk After Mitigation:**
| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 1 - Remote | 2 - Marginal | **2 (GREEN)** |

**Risk Owner:** Development Team
**Target Resolution:** Post-GA (edge case)
**Monitoring:** Container deployment feedback

---

#### RSK-XPLAT-025: Large Monorepo Git Timeout

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-XPLAT-025 |
| **Category** | Operational |
| **Description** | Git timeout is hardcoded at 2 seconds. Large monorepos with slow disk I/O may exceed this timeout, causing git segment to silently fail. |
| **Root Cause** | Fixed timeout not suitable for all repository sizes |
| **Likelihood** | 2 - Unlikely |
| **Consequence** | 3 - Moderate |
| **Risk Score** | **6 (YELLOW)** |
| **Evidence** | e-006 Section 2.3: "2-second timeout is sufficient: Large repos with slow disk may exceed this" |

**Potential Impact:**
- Git segment disappears in large repositories
- Inconsistent behavior based on repository size
- User confusion about missing git information

**Mitigation Strategy:**
1. **Immediate**: Document timeout limitation for large repos
2. **Short-term**: Make timeout configurable in config file (already exists: `advanced.git_timeout`)
3. **Long-term**: Consider async git operations if feasible

**Residual Risk After Mitigation:**
| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 1 - Remote | 2 - Marginal | **2 (GREEN)** |

**Risk Owner:** Development Team
**Target Resolution:** Already mitigated (configurable)
**Monitoring:** Large repo user feedback

---

#### RSK-XPLAT-026: Non-UTF8 Locale Handling

| Attribute | Value |
|-----------|-------|
| **Risk ID** | RSK-XPLAT-026 |
| **Category** | Operational |
| **Description** | Systems with non-UTF8 locales (LANG=C, POSIX, legacy Windows) may have encoding issues with git output, file I/O, or terminal output. |
| **Root Cause** | UTF-8 encoding hardcoded without locale detection |
| **Likelihood** | 4 - Probable |
| **Consequence** | 1 - Minimal |
| **Risk Score** | **4 (GREEN)** |
| **Evidence** | e-006 Section 3.2: "Non-UTF8 system locale: LANG=C or legacy Windows locales" |

**Potential Impact:**
- Encoding errors with non-ASCII git output
- File read/write failures on edge cases
- Garbled characters in output

**Mitigation Strategy:**
1. **Immediate**: Document UTF-8 requirement
2. **Short-term**: Add encoding error handling with fallback
3. **Long-term**: Consider locale-aware encoding detection

**Residual Risk After Mitigation:**
| Likelihood | Consequence | Score |
|------------|-------------|-------|
| 2 - Unlikely | 1 - Minimal | **2 (GREEN)** |

**Risk Owner:** Development Team
**Target Resolution:** Post-GA (low impact)
**Monitoring:** Encoding error reports

---

## Risk Monitoring Plan

### Monitoring Framework

| Risk Level | Review Frequency | Escalation Path |
|------------|------------------|-----------------|
| RED (15-25) | Weekly | Project Lead immediately |
| YELLOW (6-12) | Bi-weekly | Project Lead at next standup |
| GREEN (1-5) | Monthly | No escalation required |

### Key Risk Indicators (KRIs)

| KRI | Threshold | Action |
|-----|-----------|--------|
| Platform-specific bug reports | > 3/week | Escalate to RED |
| CI/CD failure rate | > 10% | Investigate immediately |
| User support requests | > 5/week same issue | Create new risk entry |
| Documentation gaps identified | Any critical | Add to risk register |

### Risk Review Checklist

**Weekly (RED risks):**
- [ ] RSK-XPLAT-001: Windows testing status
- [ ] RSK-XPLAT-003: Alpine Linux testing status
- [ ] RSK-XPLAT-007: CI/CD implementation status
- [ ] RSK-XPLAT-009: Emoji fallback implementation
- [ ] RSK-XPLAT-021: Uninstall documentation status

**Bi-weekly (YELLOW risks):**
- [ ] All mitigation progress tracked
- [ ] User feedback reviewed for new risks
- [ ] CI/CD test results analyzed
- [ ] Documentation gaps assessed

**Monthly (GREEN risks):**
- [ ] All risks reviewed for status changes
- [ ] Residual risk assumptions validated
- [ ] New risk identification session

---

## Appendix A: Risk Scoring Matrix Reference

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
| 6-12 | YELLOW | Mitigate before GA |
| 15-25 | RED | Block deployment until resolved |

---

## Appendix B: Traceability Matrix

| Risk ID | Gap Analysis Ref | Adversarial Critique Ref | Code Ref |
|---------|------------------|-------------------------|----------|
| RSK-XPLAT-001 | e-003 2.1 | e-006 2.2 | - |
| RSK-XPLAT-002 | e-003 2.1 | e-006 5.3 | - |
| RSK-XPLAT-003 | - | e-006 1.1, 7.2 | - |
| RSK-XPLAT-004 | - | e-006 1.2 | - |
| RSK-XPLAT-005 | - | e-006 1.1 | - |
| RSK-XPLAT-006 | e-003 3.2 | - | - |
| RSK-XPLAT-007 | e-003 2.1 | e-006 5.4 | - |
| RSK-XPLAT-008 | e-003 1.5 | e-006 2.4 | L249-258 |
| RSK-XPLAT-009 | - | e-006 7 | L672-681 |
| RSK-XPLAT-010 | e-003 2.2 | e-006 2.4 | L261-266 |
| RSK-XPLAT-011 | - | e-006 1.2 | - |
| RSK-XPLAT-012 | - | e-006 4.2 | - |
| RSK-XPLAT-013 | e-003 4.2 | e-006 2.3 | L553-587 |
| RSK-XPLAT-014 | e-003 4.1 | - | L1 |
| RSK-XPLAT-015 | - | e-006 4.1 | L37 |
| RSK-XPLAT-016 | - | e-006 4.3 | L274-282 |
| RSK-XPLAT-017 | e-003 1.4 | - | L207-210 |
| RSK-XPLAT-018 | - | e-006 6.2 | L932-941 |
| RSK-XPLAT-019 | e-003 3.1 | e-006 6.1 | - |
| RSK-XPLAT-020 | - | e-006 6.3 | - |
| RSK-XPLAT-021 | - | e-006 6.1 | - |
| RSK-XPLAT-022 | - | e-006 3.1 | L236-241 |
| RSK-XPLAT-023 | - | e-006 3.2 | L176-182 |
| RSK-XPLAT-024 | - | e-006 3.1 | L236-241 |
| RSK-XPLAT-025 | - | e-006 2.3 | L547 |
| RSK-XPLAT-026 | - | e-006 3.2 | - |

---

## Appendix C: Mitigation Priority Summary

### Immediate Actions (Before Any Release)

| Priority | Risk ID | Action | Effort |
|----------|---------|--------|--------|
| 1 | RSK-XPLAT-007 | Create GitHub Actions CI/CD | 2h |
| 2 | RSK-XPLAT-001 | Execute Windows tests | 4h |
| 3 | RSK-XPLAT-002 | Execute Linux tests | 4h |
| 4 | RSK-XPLAT-003 | Test Alpine Linux/Docker | 2h |
| 5 | RSK-XPLAT-019 | Add Linux documentation | 2h |

### Short-term Actions (Before GA)

| Priority | Risk ID | Action | Effort |
|----------|---------|--------|--------|
| 6 | RSK-XPLAT-009 | Implement ASCII emoji fallback | 2h |
| 7 | RSK-XPLAT-006 | Document WSL vs native Windows | 1h |
| 8 | RSK-XPLAT-008 | Add color disable option | 1h |
| 9 | RSK-XPLAT-012 | Implement NO_COLOR support | 0.5h |
| 10 | RSK-XPLAT-021 | Add uninstall documentation | 0.5h |

### Long-term Actions (Post-GA)

| Priority | Risk ID | Action | Effort |
|----------|---------|--------|--------|
| 11 | RSK-XPLAT-005 | ARM platform testing | 4h |
| 12 | RSK-XPLAT-022 | Implement atomic state writes | 2h |
| 13 | RSK-XPLAT-016 | Add schema version checking | 2h |

**Total Immediate Effort:** 14 hours
**Total Short-term Effort:** 5 hours
**Total Long-term Effort:** 8 hours

---

*Risk register generated by nse-risk v1.0.0*
*Based on NASA NPR 8000.4C 5x5 Risk Matrix methodology*
