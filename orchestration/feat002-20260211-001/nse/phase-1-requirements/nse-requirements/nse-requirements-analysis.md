# FEAT-002 Requirements Analysis
## ECW Status Line - High-Priority Improvements (Phase 2)

**Document ID:** FEAT-002-REQ-001
**Version:** 1.0
**Date:** 2026-02-11
**Project:** jerry-statusline (ECW Status Line v2.1.0)
**Feature:** FEAT-002 - High-Priority Improvements (Phase 2)
**Parent Epic:** EPIC-001 - Cross-Platform Compatibility
**Standards:** NPR 7123.1D (NASA Requirements Engineering)
**Agent:** nse-requirements v2.2.0

---

## Executive Summary

This requirements analysis defines the remaining work for FEAT-002 (High-Priority Improvements) of the ECW Status Line project. Following EN-002's completion of critical gaps (G-009, G-010, G-011, G-012, G-015), this document addresses the remaining code hardening and documentation tasks across two enablers:

- **EN-003: Code Hardening** (3 tasks remaining)
- **EN-004: Documentation Completion** (4 tasks remaining)

**Total Requirements:** 7 SHALL statements
**Scope:** Code robustness and documentation completeness for cross-platform deployment

---

## Table of Contents

1. [Requirements Overview](#requirements-overview)
2. [Requirements Specifications](#requirements-specifications)
3. [Traceability Matrix](#traceability-matrix)
4. [Acceptance Criteria](#acceptance-criteria)
5. [Priority Classification](#priority-classification)
6. [Verification Methods](#verification-methods)
7. [Dependencies and Assumptions](#dependencies-and-assumptions)
8. [Risks and Mitigations](#risks-and-mitigations)

---

## 1. Requirements Overview

### 1.1 Context

The ECW Status Line is a single-file Python script (statusline.py) providing real-time visibility into Claude Code session state. FEAT-002 addresses cross-platform compatibility gaps identified in the audit report (work/EPIC-001-cross-platform-compatibility/audit-report-2026-02-06.md).

**Progress to Date:**
- EN-002 completed 5 critical gaps (G-009, G-010, G-011, G-012, G-015)
- EN-003 has 3 remaining tasks (TASK-001, TASK-003, TASK-004)
- EN-004 has 4 remaining tasks (TASK-003, TASK-005, TASK-006, TASK-007)

### 1.2 Scope

This requirements analysis covers:

**In Scope:**
- Subprocess encoding parameters (G-007)
- ASCII emoji fallback completion (G-014)
- VS Code terminal testing (G-008)
- Claude Code JSON schema documentation (G-013)
- WSL vs native Windows guidance
- CI status badge
- Version changelog updates

**Out of Scope (Already Addressed by EN-002):**
- Missing HOME variable handling (G-009) - Completed
- Linux installation documentation (G-010) - Completed
- Container deployment documentation (G-011) - Completed
- Platform exclusions (G-012) - Completed
- Uninstall documentation (G-015) - Completed

### 1.3 Document Structure

This document follows NPR 7123.1D requirements engineering practices:
- SHALL statements for mandatory requirements
- Traceability to source gaps
- Acceptance criteria for verification
- Priority classification (Must-Have, Should-Have, Nice-to-Have)

---

## 2. Requirements Specifications

### EN-003: Code Hardening Requirements

#### REQ-001: Subprocess Encoding Parameter

**Source Gap:** G-007 (Non-UTF8 locale handling in subprocess)

**Requirement:**
The system SHALL specify `encoding='utf-8'` and `errors='replace'` parameters for all `subprocess.run()` calls in the `get_git_info()` function (statusline.py lines 606-612 and 623-628) to ensure consistent text decoding across all system locales.

**Rationale:**
Current implementation uses `text=True` which defaults to system locale encoding (e.g., cp1252 on Windows, shift_jis on Japanese systems). This causes UnicodeDecodeError when git output contains non-ASCII characters (e.g., author names, branch names with accents).

**Implementation Details:**
- Modify subprocess.run() at line 606 (git rev-parse)
- Modify subprocess.run() at line 623 (git status)
- Replace `text=True` with `encoding='utf-8', errors='replace'`
- Preserve existing `capture_output=True` and `timeout=timeout` parameters

**Example:**
```python
# Before:
result = subprocess.run(
    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
    cwd=cwd,
    capture_output=True,
    text=True,  # Uses system locale
    timeout=timeout,
)

# After:
result = subprocess.run(
    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
    cwd=cwd,
    capture_output=True,
    encoding='utf-8',
    errors='replace',
    timeout=timeout,
)
```

---

#### REQ-002: ASCII Emoji Fallback Completion

**Source Gap:** G-014 (Emoji ASCII fallback incomplete)

**Requirement:**
The system SHALL replace all Unicode visual characters with ASCII equivalents when `use_emoji: false` is configured, including progress bar characters (▓→#, ░→-), git status indicators (✓→+, ●→*), and token direction arrows (→→>, ↺→<).

**Rationale:**
Current implementation disables emoji icons but retains Unicode box-drawing characters for progress bars and git status indicators, causing display issues on ASCII-only terminals (e.g., certain Windows Command Prompt configurations, legacy SSH sessions, CI logs).

**Implementation Details:**

1. **Progress Bar Characters** (format_progress_bar function, line 647)
   - When `use_emoji: false`: Use `filled_char='#'` and `empty_char='-'`
   - Update DEFAULT_CONFIG to specify ASCII fallback chars

2. **Git Status Indicators** (build_git_segment function, line 858)
   - Clean status: `✓` → `+` (line 872)
   - Dirty status: `●` → `*` (line 876)

3. **Token Direction Arrows** (build_tokens_segment function, line 775)
   - Fresh tokens: `→` → `>`
   - Cached tokens: `↺` → `<`

4. **Compaction Indicator** (build_compaction_segment function, line 815)
   - Arrow: `→` → `>`

**Configuration Example:**
```json
{
  "display": {
    "use_emoji": false,
    "progress_bar": {
      "filled_char": "#",
      "empty_char": "-"
    }
  }
}
```

**Expected Output (ASCII mode):**
```
Sonnet | [####------] 42% | $1.23 | 8.5k> 45.2k< | main + | ~/project
```

---

#### REQ-003: VS Code Terminal Compatibility Testing

**Source Gap:** G-008 (VS Code terminal testing not performed)

**Requirement:**
The system SHALL be tested in VS Code integrated terminal on all supported platforms (macOS, Windows, Linux) and any identified display issues SHALL be documented in GETTING_STARTED.md under a "Known Issues" section.

**Rationale:**
VS Code integrated terminal uses different ANSI escape sequence handling than standalone terminals. Many users run Claude Code within VS Code, making this a critical compatibility requirement.

**Test Platforms:**
1. **macOS**: VS Code 1.85+ with default terminal
2. **Windows**: VS Code 1.85+ with PowerShell integrated terminal
3. **Linux**: VS Code 1.85+ with bash integrated terminal

**Test Scenarios:**
- Emoji rendering (8 distinct icons visible)
- ANSI 256-color display (green/yellow/red thresholds)
- Progress bar rendering (filled/empty characters)
- Git status indicators (✓ clean, ● dirty)
- Unicode token arrows (→ ↺)

**Acceptance:**
- If all scenarios pass: Document "VS Code integrated terminal: Supported"
- If issues found: Document workarounds (e.g., "Use `use_emoji: false` for VS Code on Windows")

---

### EN-004: Documentation Completion Requirements

#### REQ-004: Claude Code JSON Schema Documentation

**Source Gap:** G-013 (Claude Code JSON schema dependency)

**Requirement:**
The system documentation SHALL include a section describing the expected JSON schema input from Claude Code, including all required fields, optional fields, and version compatibility notes.

**Rationale:**
statusline.py depends on a specific JSON payload structure from Claude Code stdin. Changes to this schema (e.g., field renames, new fields) can break the status line. Users need to understand this dependency for troubleshooting and version compatibility.

**Implementation Location:**
New file: `docs/CLAUDE_CODE_SCHEMA.md`

**Required Content:**

1. **Schema Version**
   - Claude Code version tested (e.g., "Compatible with Claude Code v1.5.x")
   - Last verified date

2. **Required Fields**
   ```json
   {
     "model": {
       "display_name": "string",
       "id": "string"
     },
     "context_window": {
       "context_window_size": "number",
       "current_usage": {
         "input_tokens": "number",
         "cache_creation_input_tokens": "number",
         "cache_read_input_tokens": "number"
       },
       "total_input_tokens": "number",
       "total_output_tokens": "number"
     },
     "cost": {
       "total_cost_usd": "number",
       "total_duration_ms": "number"
     },
     "workspace": {
       "current_dir": "string"
     }
   }
   ```

3. **Optional Fields**
   - `transcript_path`: Required for tools segment
   - `cwd`: Fallback for workspace.current_dir

4. **Known Schema Issues**
   - Context window bug (#13783): cumulative tokens exceed window after compaction
   - Workaround: Use `current_usage` fields when available

5. **Version Compatibility Table**
   | Claude Code Version | Status | Notes |
   |---------------------|--------|-------|
   | 1.5.x | Tested | All features supported |
   | 1.4.x | Compatible | Tools segment requires 1.5+ |
   | 1.3.x | Not tested | May work with degraded features |

**Cross-Reference:**
- Link from README.md "Known Limitations" section
- Link from GETTING_STARTED.md "Troubleshooting" section

---

#### REQ-005: WSL vs Native Windows Guidance

**Source Gap:** Implicit from EN-004 TASK-005

**Requirement:**
The GETTING_STARTED.md Windows installation section SHALL include a note clarifying when to use WSL vs native Windows installation, with decision criteria based on user's Claude Code environment.

**Rationale:**
Users with Windows can run Claude Code in either native PowerShell or WSL bash. The installation instructions differ, and users need guidance on which to choose.

**Implementation:**

Add to GETTING_STARTED.md after "### Windows" heading:

```markdown
### Windows

> **WSL vs Native Windows:**
> - If you run `claude` in PowerShell: Follow the **Windows** instructions below
> - If you run `claude` in WSL bash: Follow the **Linux** instructions instead
> - **How to check:** Open your Claude Code terminal and run `echo $SHELL`:
>   - If you see `/bin/bash` or `/bin/zsh`: Use Linux instructions
>   - If you see an error or blank: Use Windows instructions
```

**Decision Criteria Table:**

| Claude Code Environment | Installation Guide | Python Command |
|------------------------|-------------------|----------------|
| PowerShell (native) | Windows section | `python` |
| WSL Ubuntu/Debian | Linux section | `python3` |
| WSL Fedora/RHEL | Linux section | `python3` |
| Git Bash (MinGW) | Windows section | `python` |

---

#### REQ-006: CI Status Badge

**Source Gap:** Implicit from EN-004 TASK-006

**Requirement:**
The README.md SHALL display a GitHub Actions CI status badge linking to the test.yml workflow to provide immediate visibility into build/test status.

**Rationale:**
Users and contributors need to see at-a-glance whether the current codebase passes tests on all supported platforms (macOS, Windows, Linux with Python 3.9-3.12).

**Implementation:**

Add to README.md after the title (line 3):

```markdown
# ECW Status Line

[![CI Status](https://github.com/geekatron/jerry-statusline/actions/workflows/test.yml/badge.svg)](https://github.com/geekatron/jerry-statusline/actions/workflows/test.yml)

**Evolved Claude Workflow** - A single-file, self-contained status line...
```

**Badge Format:**
- **Image URL:** `https://github.com/geekatron/jerry-statusline/actions/workflows/test.yml/badge.svg`
- **Link URL:** `https://github.com/geekatron/jerry-statusline/actions/workflows/test.yml`
- **Alt Text:** "CI Status"

**Expected Appearance:**
- Green "passing" badge when all tests pass on main branch
- Red "failing" badge when any tests fail
- Clicking badge navigates to workflow runs page

---

#### REQ-007: Version Changelog Update

**Source Gap:** Implicit from EN-004 TASK-007

**Requirement:**
The README.md "Version History" section SHALL be updated to reflect all changes delivered in v2.1.0, including new features, bug fixes, and compatibility improvements from FEAT-002.

**Rationale:**
The current v2.1.0 changelog (README.md lines 320-329) describes initial v2.1.0 features but does not reflect FEAT-002 improvements (cross-platform hardening, documentation updates).

**Implementation:**

Update README.md "Version History" section (line 322):

```markdown
- **2.1.0** - User experience improvements + cross-platform hardening
  - Configurable currency symbol (supports CAD, EUR, etc.)
  - New Tokens segment showing fresh→ cached↺ breakdown
  - New Session segment showing duration + total tokens
  - Compaction detection with token delta display
  - Removed 5-hour session block (not useful for long sessions)
  - Removed cache efficiency percentage (always 99%)
  - **Cross-platform improvements:**
    - UTF-8 encoding for git subprocess calls (fixes non-ASCII characters)
    - Complete ASCII emoji fallback mode (supports legacy terminals)
    - VS Code integrated terminal compatibility tested
    - WSL vs native Windows installation guidance
    - Container deployment with graceful HOME/read-only FS handling
    - Linux installation documentation (Ubuntu, Debian, Fedora, RHEL)
    - Comprehensive platform support table
    - Uninstall instructions for all platforms
  - 12 comprehensive tests
  - CI testing on macOS, Windows, Linux (Python 3.9-3.12)
```

**Changelog Principles:**
- User-facing changes first (features, UX)
- Technical improvements second (robustness, compatibility)
- Testing and infrastructure last (CI, test coverage)
- Group related changes with sub-bullets

---

## 3. Traceability Matrix

| Requirement ID | Description | Source Gap(s) | Enabler | Task(s) | Verification Method |
|---------------|-------------|---------------|---------|---------|---------------------|
| REQ-001 | Subprocess encoding parameter | G-007 | EN-003 | TASK-001 | Code inspection, test |
| REQ-002 | ASCII emoji fallback completion | G-014 | EN-003 | TASK-003 | Manual test, CI test |
| REQ-003 | VS Code terminal compatibility | G-008 | EN-003 | TASK-004 | Manual test, documentation |
| REQ-004 | Claude Code JSON schema docs | G-013 | EN-004 | TASK-003 | Documentation review |
| REQ-005 | WSL vs native Windows guidance | - | EN-004 | TASK-005 | Documentation review |
| REQ-006 | CI status badge | - | EN-004 | TASK-006 | Visual verification |
| REQ-007 | Version changelog update | - | EN-004 | TASK-007 | Documentation review |

**Gap Coverage:**
- G-007: Non-UTF8 locale handling → REQ-001
- G-008: VS Code terminal testing → REQ-003
- G-013: Claude Code JSON schema → REQ-004
- G-014: Emoji ASCII fallback → REQ-002

**Gaps Already Addressed (Not in this analysis):**
- G-009: Missing HOME variable → Completed in EN-002
- G-010: Linux installation docs → Completed in EN-002
- G-011: Container deployment docs → Completed in EN-002
- G-012: Platform exclusions → Completed in EN-002
- G-015: Uninstall documentation → Completed in EN-002

---

## 4. Acceptance Criteria

### 4.1 EN-003: Code Hardening Acceptance Criteria

#### AC-001: Subprocess Encoding (REQ-001)

**Criteria:**
- [ ] `subprocess.run()` at line 606 includes `encoding='utf-8', errors='replace'`
- [ ] `subprocess.run()` at line 623 includes `encoding='utf-8', errors='replace'`
- [ ] `text=True` parameter removed from both calls
- [ ] Git branch names with accented characters (e.g., "fiché-1") display correctly
- [ ] No UnicodeDecodeError exceptions on non-UTF8 locales (Windows cp1252, Japanese shift_jis)

**Verification Test:**
```bash
# Test on Windows with non-UTF8 locale
$env:LC_ALL = "C"
git checkout -b "test-café-123"
echo '{"model":{"display_name":"Test"},"workspace":{"current_dir":"."}}' | python statusline.py
# Expected: Branch name displays as "test-café-123" or "test-caf?-123" (not crash)
```

---

#### AC-002: ASCII Emoji Fallback (REQ-002)

**Criteria:**
- [ ] Progress bar uses `#` and `-` characters when `use_emoji: false`
- [ ] Git clean status shows `+` instead of `✓`
- [ ] Git dirty status shows `*` instead of `●`
- [ ] Token fresh indicator shows `>` instead of `→`
- [ ] Token cached indicator shows `<` instead of `↺`
- [ ] Compaction arrow shows `>` instead of `→`
- [ ] No Unicode characters (U+0080 to U+FFFF) in output when `use_emoji: false`

**Verification Test:**
```bash
# Create config with use_emoji: false
cat > ~/.claude/ecw-statusline-config.json << 'EOF'
{
  "display": {
    "use_emoji": false
  }
}
EOF

# Run statusline
echo '{"model":{"display_name":"Test"},"context_window":{"context_window_size":200000,"current_usage":{"input_tokens":42000,"cache_creation_input_tokens":0,"cache_read_input_tokens":0}},"cost":{"total_cost_usd":1.23,"total_duration_ms":60000}}' | python3 statusline.py

# Expected output (all ASCII):
# Test | [####------] 21% | $1.23 | ~/project

# Verify no Unicode characters:
python3 statusline.py < test.json | od -A x -t x1z | grep -v "00 20 2d 23 2b 2a 3e 3c"
# Expected: No output (all chars in ASCII range)
```

---

#### AC-003: VS Code Terminal Compatibility (REQ-003)

**Criteria:**
- [ ] Tested on macOS VS Code 1.85+ integrated terminal
- [ ] Tested on Windows VS Code 1.85+ PowerShell integrated terminal
- [ ] Tested on Linux VS Code 1.85+ bash integrated terminal
- [ ] Emoji rendering results documented in GETTING_STARTED.md "Known Issues" section
- [ ] ANSI color display results documented
- [ ] Workarounds provided for any identified issues

**Test Procedure:**
1. Open VS Code on target platform
2. Open integrated terminal (Ctrl+` or Cmd+`)
3. Run Claude Code: `claude`
4. Verify status line display:
   - 8 emoji icons render correctly (not boxes/question marks)
   - Colors visible (green/yellow/red)
   - Progress bar renders correctly
   - Git status indicators visible
5. Document results in GETTING_STARTED.md

**Documentation Format:**
```markdown
### VS Code Integrated Terminal

| Platform | Status | Notes |
|----------|--------|-------|
| macOS | ✓ Supported | All features work |
| Windows | ⚠ Partial | Use `use_emoji: false` for better compatibility |
| Linux | ✓ Supported | All features work |
```

---

### 4.2 EN-004: Documentation Completion Acceptance Criteria

#### AC-004: Claude Code JSON Schema Documentation (REQ-004)

**Criteria:**
- [ ] New file `docs/CLAUDE_CODE_SCHEMA.md` exists
- [ ] Schema version and compatibility table present
- [ ] Required fields documented with types
- [ ] Optional fields documented
- [ ] Known schema issues (bug #13783) documented
- [ ] Linked from README.md "Known Limitations" section
- [ ] Linked from GETTING_STARTED.md "Troubleshooting" section

**Verification:**
```bash
# File exists
test -f docs/CLAUDE_CODE_SCHEMA.md && echo "PASS" || echo "FAIL"

# Links present in README
grep -q "CLAUDE_CODE_SCHEMA.md" README.md && echo "PASS" || echo "FAIL"

# Links present in GETTING_STARTED
grep -q "CLAUDE_CODE_SCHEMA.md" GETTING_STARTED.md && echo "PASS" || echo "FAIL"
```

---

#### AC-005: WSL vs Native Windows Guidance (REQ-005)

**Criteria:**
- [ ] WSL note added to GETTING_STARTED.md Windows section
- [ ] Decision criteria based on `echo $SHELL` output
- [ ] Decision table with 4+ scenarios (PowerShell, WSL Ubuntu, WSL Fedora, Git Bash)
- [ ] Clear instruction: "If bash/zsh: Use Linux section; else: Use Windows section"

**Verification:**
```bash
# Search for WSL content
grep -i "wsl" GETTING_STARTED.md && echo "PASS" || echo "FAIL"

# Verify decision criteria
grep -q "echo \$SHELL" GETTING_STARTED.md && echo "PASS" || echo "FAIL"
```

---

#### AC-006: CI Status Badge (REQ-006)

**Criteria:**
- [ ] Badge image link present in README.md (line 3-5)
- [ ] Badge links to `https://github.com/geekatron/jerry-statusline/actions/workflows/test.yml`
- [ ] Badge displays "passing" (green) when viewing on GitHub
- [ ] Clicking badge navigates to workflow runs

**Verification:**
```bash
# Badge markdown present
grep -q "!\[.*CI.*\].*badge.svg" README.md && echo "PASS" || echo "FAIL"

# Badge URL correct
grep -q "https://github.com/geekatron/jerry-statusline/actions/workflows/test.yml" README.md && echo "PASS" || echo "FAIL"
```

---

#### AC-007: Version Changelog Update (REQ-007)

**Criteria:**
- [ ] README.md "Version History" section updated for v2.1.0
- [ ] Cross-platform improvements listed (UTF-8 encoding, ASCII fallback, VS Code testing)
- [ ] Documentation improvements listed (WSL guidance, Linux docs, platform table)
- [ ] Container hardening listed (HOME handling, read-only FS)
- [ ] CI testing platforms listed (macOS, Windows, Linux, Python 3.9-3.12)

**Verification:**
```bash
# Version 2.1.0 section present
grep -A 20 "2.1.0" README.md | grep -q "Cross-platform" && echo "PASS" || echo "FAIL"

# UTF-8 encoding mentioned
grep -A 20 "2.1.0" README.md | grep -q "UTF-8" && echo "PASS" || echo "FAIL"

# ASCII fallback mentioned
grep -A 20 "2.1.0" README.md | grep -q "ASCII.*fallback" && echo "PASS" || echo "FAIL"
```

---

## 5. Priority Classification

### 5.1 Must-Have (P0)

**Definition:** Blocking issues preventing release. Must be completed before FEAT-002 can be marked "done".

| Requirement | Rationale | Impact if Missing |
|------------|-----------|-------------------|
| REQ-001 (Subprocess encoding) | Crashes on non-UTF8 systems (e.g., Japanese Windows) | UnicodeDecodeError crashes when git output contains non-ASCII |
| REQ-002 (ASCII fallback) | Unusable on ASCII-only terminals | Display corruption on legacy systems, CI logs unreadable |

**Completion Criteria:**
- All Must-Have requirements verified via acceptance criteria
- No known crashes or display corruption on supported platforms

---

### 5.2 Should-Have (P1)

**Definition:** Important for quality but not blocking. Should be completed before release but can be deferred if timeline at risk.

| Requirement | Rationale | Impact if Missing |
|------------|-----------|-------------------|
| REQ-003 (VS Code testing) | Many users run Claude Code in VS Code | Unknown compatibility issues with popular environment |
| REQ-004 (JSON schema docs) | Critical for troubleshooting version mismatches | Users cannot debug schema-related issues |
| REQ-005 (WSL guidance) | Prevents user confusion on Windows | Windows users waste time with wrong installation method |

**Deferral Criteria:**
- If REQ-003 finds no issues: Document "Not tested" in Known Issues
- If REQ-004 timeline slips: Create GitHub issue for v2.2.0
- If REQ-005 timeline slips: Add inline note "WSL users: see Linux section"

---

### 5.3 Nice-to-Have (P2)

**Definition:** Quality-of-life improvements. Can be completed in a follow-up release without impact.

| Requirement | Rationale | Impact if Missing |
|------------|-----------|-------------------|
| REQ-006 (CI badge) | Visual indication of build status | Users can still check CI by visiting Actions page manually |
| REQ-007 (Changelog update) | Completeness of release notes | v2.1.0 features already documented, missing only FEAT-002 details |

**Deferral Criteria:**
- Can be completed post-release in a documentation-only commit
- No functional impact

---

### 5.4 Priority Summary Table

| Priority | Requirements | Total | Estimated Effort |
|----------|-------------|-------|-----------------|
| P0 (Must-Have) | REQ-001, REQ-002 | 2 | 4h |
| P1 (Should-Have) | REQ-003, REQ-004, REQ-005 | 3 | 5h |
| P2 (Nice-to-Have) | REQ-006, REQ-007 | 2 | 1h |
| **TOTAL** | | **7** | **10h** |

**Note:** Original EN-003 + EN-004 estimate was 18h (7h + 11h). This analysis scopes 10h of remaining work after EN-002 completion, consistent with task re-assessment.

---

## 6. Verification Methods

### 6.1 Code Inspection

**Requirements:** REQ-001, REQ-002

**Method:**
1. Review statusline.py source code
2. Verify encoding parameters present (REQ-001)
3. Verify ASCII character substitution logic (REQ-002)
4. Use static analysis: `grep -n "subprocess.run" statusline.py`

**Pass Criteria:**
- No `text=True` in subprocess.run() calls
- All subprocess.run() calls include `encoding='utf-8', errors='replace'`
- ASCII fallback characters used when `use_emoji: false`

---

### 6.2 Automated Testing

**Requirements:** REQ-001, REQ-002

**Method:**
1. Extend test_statusline.py with new test cases
2. Test subprocess encoding with non-ASCII git branch names
3. Test ASCII fallback mode output

**New Test Cases:**

```python
def test_subprocess_encoding_utf8():
    """Verify subprocess calls use UTF-8 encoding."""
    # This test verifies the parameter is present, actual encoding tested manually
    with open('statusline.py', 'r') as f:
        code = f.read()
    assert "encoding='utf-8'" in code
    assert "errors='replace'" in code

def test_ascii_fallback_mode():
    """Verify ASCII-only output when use_emoji: false."""
    config = {"display": {"use_emoji": False}}
    # ... (test logic to verify no Unicode chars in output)
```

**Pass Criteria:**
- All existing tests pass (12 tests)
- New tests pass (2 additional tests)
- CI runs on Python 3.9-3.12 across macOS, Windows, Linux

---

### 6.3 Manual Testing

**Requirements:** REQ-003 (VS Code testing)

**Method:**
1. Install VS Code 1.85+ on macOS, Windows, Linux
2. Open integrated terminal
3. Run Claude Code and verify status line display
4. Document results

**Test Matrix:**

| Platform | VS Code Version | Terminal | Python Version | Tester | Status |
|----------|----------------|----------|----------------|--------|--------|
| macOS 14 | 1.85.0 | zsh | 3.11 | TBD | Pending |
| Windows 11 | 1.85.0 | PowerShell | 3.11 | TBD | Pending |
| Ubuntu 22.04 | 1.85.0 | bash | 3.11 | TBD | Pending |

**Pass Criteria:**
- At least one test per platform completed
- Results documented in GETTING_STARTED.md

---

### 6.4 Documentation Review

**Requirements:** REQ-004, REQ-005, REQ-006, REQ-007

**Method:**
1. Peer review of documentation changes
2. Verify completeness against acceptance criteria
3. Check for broken links, typos, formatting issues

**Review Checklist:**
- [ ] docs/CLAUDE_CODE_SCHEMA.md complete and accurate
- [ ] WSL guidance clear and actionable
- [ ] CI badge displays correctly on GitHub
- [ ] Changelog accurately reflects v2.1.0 changes
- [ ] All cross-references valid (no broken links)
- [ ] Markdown renders correctly on GitHub

**Pass Criteria:**
- All checklist items complete
- No reviewer-identified defects

---

## 7. Dependencies and Assumptions

### 7.1 Dependencies

**Internal Dependencies:**
- EN-002 completion (VERIFIED: Completed as of 2026-02-11)
- statusline.py v2.1.0 baseline code
- test_statusline.py baseline tests
- GETTING_STARTED.md baseline documentation

**External Dependencies:**
- Claude Code CLI version 1.5.x (JSON schema compatibility)
- Git 2.x (for subprocess testing)
- Python 3.9+ (minimum version)
- GitHub Actions (for CI badge)

**Toolchain Dependencies:**
- uv (Python package manager) - per CLAUDE.md project rules
- ruff (linting/formatting) - for code quality checks

---

### 7.2 Assumptions

**Technical Assumptions:**
1. Claude Code JSON schema remains stable (no breaking changes in 1.5.x)
2. Git output encoding is consistent within a given locale
3. VS Code integrated terminal supports same ANSI sequences as standalone terminals
4. ASCII characters (0x20-0x7E) render correctly on all terminals

**Process Assumptions:**
1. Requirements can be implemented independently (no blocking dependencies between REQ-001 to REQ-007)
2. Manual testing (REQ-003) can be completed within 2h per platform
3. Documentation changes do not require code changes (REQ-004 to REQ-007)

**Risk Assumptions:**
1. No new gaps discovered during implementation
2. CI pipeline remains stable (no GitHub Actions outages)
3. Test coverage sufficient to catch regressions

---

### 7.3 Constraints

**Time Constraints:**
- EN-003 due: 2026-02-21 (10 days remaining)
- EN-004 due: 2026-02-21 (10 days remaining)
- Total effort: 10h (1.25 developer-days)

**Scope Constraints:**
- No changes to statusline.py core logic (only hardening)
- No new features (only cross-platform compatibility)
- No changes to configuration schema (backward compatible)

**Platform Constraints:**
- Testing limited to Python 3.9-3.12 (no 3.8 or 3.13+)
- Testing limited to macOS 12+, Windows 10+, Ubuntu 22.04+ (per audit report)
- No Alpine Linux testing (musl libc not supported)

---

## 8. Risks and Mitigations

### 8.1 Technical Risks

#### RISK-001: VS Code Terminal Incompatibility

**Risk:** VS Code integrated terminal may not support ANSI 256-color or Unicode emoji, requiring fallback mode by default.

**Probability:** Low
**Impact:** Medium (degraded UX for VS Code users)

**Mitigation:**
- Document workaround in GETTING_STARTED.md immediately upon discovery
- Provide `use_emoji: false` config example for VS Code users
- Consider auto-detection of VS Code environment in future release (out of scope for FEAT-002)

**Contingency:**
- If widespread issues: Make ASCII mode default for Windows VS Code

---

#### RISK-002: Subprocess Encoding Edge Cases

**Risk:** `encoding='utf-8', errors='replace'` may not handle all edge cases (e.g., binary data in git output, malformed UTF-8 sequences).

**Probability:** Low
**Impact:** Low (graceful degradation with `?` replacement characters)

**Mitigation:**
- Use `errors='replace'` to substitute invalid sequences with `?` rather than crashing
- Add debug logging for encoding errors
- Document known limitations in CLAUDE_CODE_SCHEMA.md

**Contingency:**
- If crashes occur: Add additional try/except around subprocess calls
- If `?` characters problematic: Add `errors='ignore'` config option

---

#### RISK-003: ASCII Fallback Incomplete

**Risk:** Undiscovered Unicode characters in output when `use_emoji: false` (e.g., in tool names, directory paths).

**Probability:** Low
**Impact:** Low (isolated display corruption)

**Mitigation:**
- Add automated test to scan output for non-ASCII bytes
- Test with diverse input data (non-English paths, tool names with Unicode)

**Contingency:**
- If found: Add to REQ-002 acceptance criteria and fix before release

---

### 8.2 Documentation Risks

#### RISK-004: Claude Code Schema Changes

**Risk:** Claude Code schema changes between 1.5.x releases, invalidating REQ-004 documentation.

**Probability:** Medium
**Impact:** Medium (outdated troubleshooting docs)

**Mitigation:**
- Include "Last Verified" date in CLAUDE_CODE_SCHEMA.md
- Add note: "Schema subject to change. Report issues at GitHub."
- Test against latest Claude Code version before release

**Contingency:**
- If schema changes: Update docs in patch release (v2.1.1)
- If breaking changes: Document migration path

---

#### RISK-005: WSL Guidance Ambiguity

**Risk:** WSL vs native Windows guidance too complex, users choose wrong installation method.

**Probability:** Low
**Impact:** Low (user can retry with correct method)

**Mitigation:**
- Use decision tree format (if X then Y)
- Provide concrete test command: `echo $SHELL`
- Add troubleshooting section for wrong-method scenarios

**Contingency:**
- If user reports confusion: Add video walkthrough link
- If high error rate: Add auto-detection script

---

### 8.3 Schedule Risks

#### RISK-006: Manual Testing Delays

**Risk:** VS Code testing (REQ-003) delayed due to platform access issues or tester availability.

**Probability:** Medium
**Impact:** Low (can defer to Should-Have)

**Mitigation:**
- Start testing early (parallel with code changes)
- Use personal devices for initial testing
- Document "Tested on: macOS only" if other platforms unavailable

**Contingency:**
- If blocked: Mark REQ-003 as "Partially Complete" and defer Windows/Linux testing to v2.2.0

---

### 8.4 Risk Summary Table

| Risk ID | Description | Probability | Impact | Priority | Mitigation Owner |
|---------|-------------|-------------|--------|----------|-----------------|
| RISK-001 | VS Code incompatibility | Low | Medium | P1 | Implementation team |
| RISK-002 | Encoding edge cases | Low | Low | P2 | Implementation team |
| RISK-003 | ASCII fallback gaps | Low | Low | P2 | QA/Testing |
| RISK-004 | Schema changes | Medium | Medium | P1 | Documentation owner |
| RISK-005 | WSL guidance ambiguity | Low | Low | P2 | Documentation owner |
| RISK-006 | Testing delays | Medium | Low | P2 | Project manager |

**Overall Risk Level:** LOW
All identified risks have low-to-medium probability and low-to-medium impact, with clear mitigations in place.

---

## Appendices

### Appendix A: Source Gap Details

**G-007: Non-UTF8 Locale Handling in Subprocess**
- **Location:** statusline.py lines 606-612, 623-628
- **Issue:** `text=True` uses system locale (cp1252, shift_jis, etc.), causing UnicodeDecodeError on non-ASCII git output
- **Fix:** Use `encoding='utf-8', errors='replace'`

**G-008: VS Code Terminal Testing Not Performed**
- **Issue:** Unknown compatibility with VS Code integrated terminal
- **Fix:** Manual testing on macOS, Windows, Linux + documentation

**G-013: Claude Code JSON Schema Dependency**
- **Issue:** No documentation of expected JSON input format
- **Fix:** Create docs/CLAUDE_CODE_SCHEMA.md with schema reference

**G-014: Emoji ASCII Fallback Incomplete**
- **Location:** Multiple functions (format_progress_bar, build_git_segment, build_tokens_segment)
- **Issue:** Unicode box-drawing chars (▓░→↺✓●) present even when `use_emoji: false`
- **Fix:** Replace with ASCII equivalents (#-+*><)

---

### Appendix B: Code Locations Reference

| Requirement | File | Line(s) | Function |
|------------|------|---------|----------|
| REQ-001 | statusline.py | 606-612 | get_git_info (git rev-parse) |
| REQ-001 | statusline.py | 623-628 | get_git_info (git status) |
| REQ-002 | statusline.py | 647-667 | format_progress_bar |
| REQ-002 | statusline.py | 858-885 | build_git_segment |
| REQ-002 | statusline.py | 775-792 | build_tokens_segment |
| REQ-002 | statusline.py | 815-834 | build_compaction_segment |
| REQ-004 | docs/ | N/A | CLAUDE_CODE_SCHEMA.md (new file) |
| REQ-005 | GETTING_STARTED.md | 124 (after "### Windows") | Windows section |
| REQ-006 | README.md | 3 (after title) | CI badge |
| REQ-007 | README.md | 320-329 | Version History |

---

### Appendix C: Verification Test Scripts

#### Test Script 1: Subprocess Encoding Verification

```bash
#!/bin/bash
# test_subprocess_encoding.sh
# Verifies REQ-001: Subprocess encoding parameter

set -e

echo "Testing subprocess encoding parameter..."

# Check that encoding parameter is present
if grep -q "encoding='utf-8'" statusline.py && grep -q "errors='replace'" statusline.py; then
    echo "✓ PASS: Encoding parameters found in code"
else
    echo "✗ FAIL: Encoding parameters missing"
    exit 1
fi

# Check that text=True is NOT present in get_git_info
if grep -A 20 "def get_git_info" statusline.py | grep -q "text=True"; then
    echo "✗ FAIL: text=True still present in get_git_info"
    exit 1
else
    echo "✓ PASS: text=True removed from get_git_info"
fi

echo "All encoding tests passed!"
```

#### Test Script 2: ASCII Fallback Verification

```bash
#!/bin/bash
# test_ascii_fallback.sh
# Verifies REQ-002: ASCII emoji fallback completion

set -e

echo "Testing ASCII fallback mode..."

# Create config with use_emoji: false
cat > /tmp/ecw-test-config.json << 'EOF'
{
  "display": {
    "use_emoji": false
  }
}
EOF

# Test with mock JSON payload
TEST_JSON='{"model":{"display_name":"Test","id":"sonnet"},"context_window":{"context_window_size":200000,"current_usage":{"input_tokens":42000,"cache_creation_input_tokens":0,"cache_read_input_tokens":0}},"cost":{"total_cost_usd":1.23,"total_duration_ms":60000},"workspace":{"current_dir":"/tmp"}}'

# Run statusline with test config
OUTPUT=$(echo "$TEST_JSON" | CONFIG_PATH=/tmp/ecw-test-config.json python3 statusline.py)

# Check for Unicode characters (should be none)
if echo "$OUTPUT" | grep -qP '[^\x00-\x7F]'; then
    echo "✗ FAIL: Unicode characters found in ASCII mode output:"
    echo "$OUTPUT" | od -A x -t x1z
    exit 1
else
    echo "✓ PASS: No Unicode characters in output"
fi

# Check for ASCII replacements
if echo "$OUTPUT" | grep -q "[#-]"; then
    echo "✓ PASS: ASCII progress bar characters present"
else
    echo "✗ FAIL: ASCII progress bar characters missing"
    exit 1
fi

echo "All ASCII fallback tests passed!"
```

---

### Appendix D: Glossary

| Term | Definition |
|------|------------|
| **SHALL** | Mandatory requirement (RFC 2119 compliance) |
| **SHOULD** | Recommended but not mandatory |
| **MAY** | Optional |
| **NPR 7123.1D** | NASA Requirements Engineering standard |
| **UTF-8** | Unicode character encoding (backward compatible with ASCII) |
| **ASCII** | 7-bit character encoding (0x00-0x7F) |
| **ANSI 256-color** | Terminal color escape sequences supporting 256 colors |
| **WSL** | Windows Subsystem for Linux |
| **glibc** | GNU C Library (standard for Linux distributions) |
| **musl** | Lightweight C library (used by Alpine Linux) |
| **Subprocess encoding** | Character encoding for decoding subprocess stdout/stderr |
| **Emoji fallback** | ASCII character substitution when Unicode emoji not supported |

---

### Appendix E: References

1. **NPR 7123.1D** - NASA Systems Engineering Processes and Requirements
   https://nodis3.gsfc.nasa.gov/displayDir.cfm?t=NPR&c=7123&s=1D

2. **RFC 2119** - Key words for use in RFCs to Indicate Requirement Levels
   https://www.ietf.org/rfc/rfc2119.txt

3. **Python subprocess encoding** - subprocess.run() documentation
   https://docs.python.org/3/library/subprocess.html#subprocess.run

4. **ANSI escape codes** - Terminal color and formatting sequences
   https://en.wikipedia.org/wiki/ANSI_escape_code

5. **ECW Status Line GitHub Repository**
   https://github.com/geekatron/jerry-statusline

6. **Claude Code Issue #13783** - Context window cumulative bug
   https://github.com/anthropics/claude-code/issues/13783

7. **ECW Status Line Audit Report** (2026-02-06)
   /Users/adam.nowak/workspace/GitHub/geekatron/jerry-statusline/work/EPIC-001-cross-platform-compatibility/audit-report-2026-02-06.md

8. **EN-002 Verification Report** (2026-02-06)
   /Users/adam.nowak/workspace/GitHub/geekatron/jerry-statusline/work/EPIC-001-cross-platform-compatibility/FEAT-001-critical-remediations/verification-report-2026-02-06.md

---

## Document Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Requirements Engineer | nse-requirements agent v2.2.0 | [Digital] | 2026-02-11 |
| Technical Reviewer | TBD | | |
| Project Manager | TBD | | |

---

## Disclaimer

**This requirements analysis was generated by nse-requirements agent (v2.2.0). Human review recommended.**

This document was created using automated requirements engineering processes following NPR 7123.1D standards. While the analysis is comprehensive and traceable, human review is recommended to:

1. Validate requirement completeness against project context
2. Verify acceptance criteria are testable and achievable
3. Confirm priority classifications align with project goals
4. Review risk assessments and mitigation strategies
5. Ensure traceability matrix accuracy

**Review Checklist for Human Reviewer:**
- [ ] All 7 requirements are necessary and sufficient
- [ ] Acceptance criteria are clear and testable
- [ ] Priority classifications (P0/P1/P2) are appropriate
- [ ] Risk mitigations are actionable
- [ ] Traceability to source gaps is accurate
- [ ] No requirements conflict or overlap
- [ ] Effort estimates (10h total) are realistic
- [ ] Verification methods are appropriate

**Document Status:** DRAFT - Pending human review and approval

---

**End of Document**
