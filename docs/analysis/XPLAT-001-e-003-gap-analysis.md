# Cross-Platform Gap Analysis for jerry-statusline

**PS ID:** XPLAT-001
**Entry ID:** e-003
**Topic:** Cross-Platform Gap Analysis
**Date:** 2026-02-03
**Analyst:** ps-analyst v2.0.0

---

## L0 - Executive Summary

The jerry-statusline project (ECW Status Line v2.1.0) has **partial cross-platform support**. It currently works well on macOS and has basic Windows support documented, but **Linux is significantly under-documented and untested**. The codebase uses Python standard library features that are mostly cross-platform, but several code patterns and documentation gaps create barriers to reliable operation on all three platforms.

### Overall Risk Assessment

| Platform | Readiness | Risk Level | Primary Gaps |
|----------|-----------|------------|--------------|
| macOS    | Production-ready | Low | Minor documentation gaps |
| Linux    | Functional but untested | Medium | No documentation, no CI testing |
| Windows  | Partial support | Medium-High | Path handling, terminal compatibility |

### Priority Remediation Summary

1. **HIGH:** Add Linux installation documentation
2. **HIGH:** Implement CI/CD multi-platform testing matrix
3. **MEDIUM:** Fix Windows path handling in settings.json command
4. **MEDIUM:** Add platform-specific test cases
5. **LOW:** Document WSL vs native Windows differences

---

## L1 - Gap Categories Analysis

### 1. Code Gaps

#### 1.1 Shebang Line Analysis

**Current Implementation:**
```python
#!/usr/bin/env python3
```

**Platform Compatibility:**

| Platform | Status | Notes |
|----------|--------|-------|
| macOS    | Works  | `/usr/bin/env` present by default |
| Linux    | Works  | `/usr/bin/env` present on all major distributions |
| Windows  | N/A    | Shebang ignored; requires explicit `python` invocation |

**Risk Level:** LOW - Not a functional issue on any platform.

**5 Whys Analysis:**
1. Why might the shebang cause issues? - It only matters for direct execution.
2. Why does direct execution matter? - The documented invocation uses `python3 ~/.claude/statusline.py` anyway.
3. Why use shebang at all? - Convenience for `chmod +x` execution on Unix systems.
4. Why not standardize? - Windows doesn't support shebang.
5. Why is this acceptable? - Cross-platform Python convention; no action needed.

**Recommendation:** No change required. Document that Windows users must use explicit `python` invocation.

---

#### 1.2 Home Directory Expansion

**Current Implementation (statusline.py lines 220, 234, 510):**
```python
state_file = Path(os.path.expanduser(config["compaction"]["state_file"]))
# Default: "~/.claude/ecw-statusline-state.json"

home = os.path.expanduser("~")
if current_dir.startswith(home):
    current_dir = "~" + current_dir[len(home):]
```

**Platform Compatibility:**

| Platform | Status | Notes |
|----------|--------|-------|
| macOS    | Works  | `~` expands to `/Users/username` |
| Linux    | Works  | `~` expands to `/home/username` |
| Windows  | Works  | `~` expands to `C:\Users\username` |

**Risk Level:** LOW - Python's `os.path.expanduser()` handles all platforms correctly.

**Evidence:** Python documentation confirms cross-platform support. The `pathlib.Path.home()` alternative is also used (line 163), which is similarly cross-platform.

**Recommendation:** No change required. Code is already cross-platform compliant.

---

#### 1.3 Path Separator Handling

**Current Implementation Analysis:**

The codebase uses two path handling approaches:

1. **pathlib.Path (Cross-platform safe):**
   ```python
   CONFIG_PATHS = [
       Path(__file__).parent / "ecw-statusline-config.json",
       Path.home() / ".claude" / "ecw-statusline-config.json",
   ]
   ```

2. **String operations (Potentially problematic):**
   ```python
   # Line 510-512
   if current_dir.startswith(home):
       current_dir = "~" + current_dir[len(home):]
   ```

**Platform Compatibility:**

| Pattern | macOS/Linux | Windows | Issue |
|---------|-------------|---------|-------|
| `pathlib.Path` / operator | Works | Works | None |
| String concatenation with `/` | Works | Works* | Display-only, acceptable |
| `os.path.basename()` | Works | Works | None |

*Windows paths using `/` work in most contexts but may display inconsistently.

**Risk Level:** LOW - String operations are for display purposes only; actual file operations use pathlib.

**5 Whys Analysis:**
1. Why might string paths cause issues? - Windows uses backslash natively.
2. Why does the code use forward slash in strings? - For `~` prefix display only.
3. Why is display different from file operations? - Display is user-facing; file ops use OS APIs.
4. Why doesn't this break Windows? - The display string is never used for file access.
5. Why is this acceptable? - Users expect Unix-style `~` in status line regardless of platform.

**Recommendation:** No change required. Consider adding a comment explaining the display-only nature of path string operations.

---

#### 1.4 Git Command Availability

**Current Implementation (statusline.py lines 553-587):**
```python
result = subprocess.run(
    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
    cwd=cwd,
    capture_output=True,
    text=True,
    timeout=timeout,
)
```

**Platform Compatibility:**

| Platform | Status | Notes |
|----------|--------|-------|
| macOS    | Works  | Git typically installed via Xcode CLT or Homebrew |
| Linux    | Works  | Git available via package manager |
| Windows  | Works* | Requires Git for Windows or git in PATH |

**Risk Level:** MEDIUM - Git availability varies; failure handling exists but user experience differs.

**Current Error Handling:**
```python
except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
    debug_log(f"Git error: {e}")
    return None
```

**Gap Identified:** Error handling silently hides git segment when git is not found. No user feedback about why git segment is missing.

**5 Whys Analysis:**
1. Why might git commands fail? - Git not installed or not in PATH.
2. Why is PATH important? - Windows Git for Windows installs to non-standard location.
3. Why does this affect users? - Segment silently disappears without explanation.
4. Why is silent failure problematic? - Users don't know if feature is disabled or broken.
5. Why hasn't this been addressed? - Design choice for clean output; documentation gap.

**Recommendation:**
1. Document git PATH requirements for each platform
2. Consider optional debug message when git is not found
3. Add troubleshooting section for git segment issues (partially exists)

---

#### 1.5 ANSI Color Support

**Current Implementation (statusline.py lines 249-258):**
```python
def ansi_color(code: int) -> str:
    """Generate ANSI 256-color escape sequence."""
    if code == 0:
        return "\033[0m"
    return f"\033[38;5;{code}m"
```

**Platform Compatibility:**

| Platform | Terminal | Status | Notes |
|----------|----------|--------|-------|
| macOS    | Terminal.app | Works | 256-color support |
| macOS    | iTerm2 | Works | Full 256-color support |
| Linux    | Most terminals | Works | TERM=xterm-256color |
| Windows  | cmd.exe | Limited | May not support ANSI |
| Windows  | PowerShell | Works* | Requires Windows 10+ |
| Windows  | Windows Terminal | Works | Full support |

**Risk Level:** MEDIUM - Windows legacy terminals may not render colors correctly.

**Gap Identified:** No detection of terminal capabilities. No fallback for terminals without ANSI support.

**Recommendation:**
1. Document Windows Terminal as recommended terminal
2. Consider adding `os.system('')` Windows ANSI enablement hack
3. Add config option to disable colors entirely (`"colors": {"enabled": false}`)

---

### 2. Test Gaps

#### 2.1 Test File Analysis (test_statusline.py)

**Current Test Coverage:**

| Test Category | Covered | Platform-Specific |
|---------------|---------|-------------------|
| Basic payload processing | Yes | No |
| Model detection (Opus/Sonnet/Haiku) | Yes | No |
| Context threshold warnings | Yes | No |
| Cost display | Yes | No |
| Compact mode | Yes | No |
| Currency configuration | Yes | No |
| Token breakdown | Yes | No |
| Session duration | Yes | No |
| Compaction detection | Yes | No |
| Tools segment | Yes | No |

**Gaps Identified:**

1. **No platform-specific test cases**
   - No tests for Windows path handling
   - No tests for Linux-specific behaviors
   - No tests for terminal capability detection

2. **No CI/CD multi-platform testing**
   - Tests only run locally on developer machine
   - No GitHub Actions workflow for cross-platform testing

3. **Hardcoded Unix paths in test payloads:**
   ```python
   PAYLOAD_NORMAL = {
       "cwd": "/home/user/ecw-statusline",  # Unix-style path
       "workspace": {
           "current_dir": "/home/user/ecw-statusline",
       },
   }
   ```

**Risk Level:** HIGH - Platform-specific bugs may go undetected until user reports.

**5 Whys Analysis:**
1. Why are there no Windows tests? - Development primarily on macOS.
2. Why does this matter? - Windows has different path semantics.
3. Why might paths differ? - `C:\Users\...` vs `/home/...`.
4. Why do test payloads use Unix paths? - Tests simulate Claude Code's JSON payload.
5. Why is this a gap? - Doesn't test Windows-specific display behaviors.

**Recommendations:**
1. Add parametrized tests with platform-specific payloads
2. Create GitHub Actions workflow with matrix strategy:
   ```yaml
   strategy:
     matrix:
       os: [ubuntu-latest, macos-latest, windows-latest]
       python-version: ['3.9', '3.10', '3.11', '3.12']
   ```
3. Add platform detection helper for conditional test assertions

---

#### 2.2 Missing Test Categories

| Test Category | Priority | Description |
|---------------|----------|-------------|
| Windows path display | HIGH | Test `C:\Users\...` abbreviation to `~\...` |
| Git on Windows | MEDIUM | Test git commands with Windows Git |
| No-git environment | MEDIUM | Test graceful degradation when git unavailable |
| Terminal width detection | LOW | Test `os.get_terminal_size()` failure handling |
| Config file encoding | MEDIUM | Test UTF-8 BOM handling on Windows |
| Emoji rendering | LOW | Cannot automate; document manual verification |

---

### 3. Documentation Gaps

#### 3.1 Linux Installation Documentation

**Current State:** MISSING

**Gap Analysis:**

GETTING_STARTED.md contains:
- macOS installation: Comprehensive (lines 25-240)
- Windows installation: Comprehensive (lines 245-300)
- Linux installation: NOT PRESENT

**Risk Level:** HIGH - Linux users have no guidance.

**5 Whys Analysis:**
1. Why is Linux not documented? - Development focus on macOS.
2. Why does this matter? - Linux is a major developer platform.
3. Why might Linux differ? - Package managers vary (apt, dnf, pacman).
4. Why is package manager important? - Python installation method differs.
5. Why is this high priority? - Easy to add, high impact for Linux users.

**Recommendation:** Add Linux section to GETTING_STARTED.md covering:
- Python installation via apt/dnf/pacman
- Git installation
- Terminal emulator requirements
- Distribution-specific notes (Ubuntu, Fedora, Arch)

---

#### 3.2 WSL vs Native Windows Documentation

**Current State:** PARTIAL

Documentation mentions Windows but doesn't distinguish:
- Native Windows PowerShell
- WSL (Windows Subsystem for Linux)
- Git Bash / MSYS2

**Gap Identified:** Users may be confused about which environment to use.

**Risk Level:** MEDIUM - Can cause installation failures.

**Recommendation:** Add section clarifying:
1. Native Windows: Use PowerShell + Windows Terminal
2. WSL: Follow Linux instructions
3. Git Bash: Follow macOS instructions with caveats

---

#### 3.3 Platform-Specific Troubleshooting

**Current Coverage Analysis:**

| Issue | macOS | Windows | Linux |
|-------|-------|---------|-------|
| Status line not appearing | Yes | Partial | No |
| Emoji rendering issues | Yes | Yes | No |
| Color issues | Yes | Partial | No |
| Git segment issues | Partial | Partial | No |
| Python version issues | Yes | Yes | No |

**Gap:** Troubleshooting section lacks Linux-specific guidance.

**Recommendation:** Expand troubleshooting with:
- Linux terminal emulator recommendations
- `TERM` environment variable configuration
- Distribution-specific Python/Git paths

---

### 4. Dependency Gaps

#### 4.1 Python Installation Differences

| Platform | Default Python | Installation Method | Notes |
|----------|----------------|---------------------|-------|
| macOS    | Python 3 (since Monterey) | Homebrew recommended | Xcode CLT also works |
| Linux    | Varies by distro | Package manager | python3 vs python |
| Windows  | None | python.org installer | PATH configuration critical |

**Gap Identified:** Linux may have `python` vs `python3` naming inconsistency.

**Risk Level:** MEDIUM

**Recommendation:**
1. Document that `python3` command is required
2. Add note about creating `python3` alias if needed on Linux
3. Consider adding shebang fallback detection in documentation

---

#### 4.2 Git Installation Differences

| Platform | Default Git | Installation Method |
|----------|-------------|---------------------|
| macOS    | Via Xcode CLT | `xcode-select --install` or Homebrew |
| Linux    | Package manager | `apt install git`, `dnf install git` |
| Windows  | None | Git for Windows installer |

**Gap:** Windows Git for Windows may not be in PATH by default.

**Recommendation:** Document PATH requirements and verification steps for all platforms.

---

#### 4.3 Terminal Emulator Requirements

| Platform | Recommended Terminal | Minimum Requirements |
|----------|---------------------|---------------------|
| macOS    | iTerm2 or Terminal.app | 256-color, emoji support |
| Linux    | GNOME Terminal, Konsole, Alacritty | 256-color, emoji font |
| Windows  | Windows Terminal | Windows 10+, ANSI support |

**Gap Identified:** Linux terminal requirements not documented.

**Recommendation:** Add section on recommended terminals for each platform with feature requirements table.

---

## L2 - Detailed Remediation Plan

### Trade-off Analysis for Remediation Approaches

#### Option A: Minimal Effort (Documentation Only)

| Pros | Cons |
|------|------|
| Fast to implement | Doesn't catch runtime issues |
| No code changes | Relies on user following docs |
| Low risk of regression | Limited automation |

**Effort:** 2-4 hours
**Impact:** Medium

#### Option B: Moderate Effort (Docs + Tests)

| Pros | Cons |
|------|------|
| Catches platform issues early | Requires CI/CD setup |
| Automated verification | More maintenance overhead |
| Higher confidence | Initial time investment |

**Effort:** 8-16 hours
**Impact:** High

#### Option C: Full Effort (Docs + Tests + Code Hardening)

| Pros | Cons |
|------|------|
| Best cross-platform support | Significant development time |
| Graceful degradation | May introduce new bugs |
| Professional polish | Over-engineering risk |

**Effort:** 24-40 hours
**Impact:** Highest

### Recommended Approach: Option B (Moderate Effort)

Provides best balance of coverage and effort for a utility tool of this scope.

---

### Implementation Roadmap

#### Phase 1: Documentation (Priority: HIGH)

**Task 1.1: Add Linux Installation Section**
- File: `GETTING_STARTED.md`
- Content: Prerequisites, installation steps, verification
- Effort: 2 hours

**Task 1.2: Add WSL Clarification**
- File: `GETTING_STARTED.md`
- Content: WSL vs native Windows guidance
- Effort: 1 hour

**Task 1.3: Expand Platform Troubleshooting**
- File: `GETTING_STARTED.md`
- Content: Linux-specific issues, terminal recommendations
- Effort: 1 hour

#### Phase 2: Testing (Priority: HIGH)

**Task 2.1: Create CI/CD Workflow**
- File: `.github/workflows/test.yml`
- Content: Multi-platform matrix with Python 3.9-3.12
- Effort: 2 hours

**Task 2.2: Add Platform-Specific Test Payloads**
- File: `test_statusline.py`
- Content: Windows path payloads, parametrized tests
- Effort: 3 hours

**Task 2.3: Add Platform Detection Tests**
- File: `test_statusline.py`
- Content: Test OS-specific behaviors
- Effort: 2 hours

#### Phase 3: Code Hardening (Priority: MEDIUM)

**Task 3.1: Add ANSI Color Toggle**
- File: `statusline.py`
- Content: Config option to disable colors
- Effort: 1 hour

**Task 3.2: Improve Error Messages**
- File: `statusline.py`
- Content: Debug messages for git not found, etc.
- Effort: 1 hour

---

## Appendix A: Evidence Summary

### Files Analyzed

1. `statusline.py` (946 lines)
2. `test_statusline.py` (623 lines)
3. `GETTING_STARTED.md` (743 lines)

### Code Patterns Identified

| Pattern | Count | Cross-Platform Safe |
|---------|-------|---------------------|
| `pathlib.Path` operations | 12 | Yes |
| `os.path.expanduser()` | 3 | Yes |
| `subprocess.run()` | 2 | Yes* |
| ANSI escape sequences | 4 | Partial |
| String path operations | 5 | Yes (display only) |

*Requires command availability

### Test Execution Platforms

Current: macOS only (inferred from development)
Required: macOS, Linux, Windows

---

## Appendix B: Quick Reference

### Gap Priority Matrix

| Gap | Severity | Effort | Priority Score |
|-----|----------|--------|----------------|
| Linux documentation | High | Low | P1 |
| CI/CD multi-platform | High | Medium | P1 |
| Windows settings.json path | Medium | Low | P2 |
| Platform-specific tests | Medium | Medium | P2 |
| WSL documentation | Medium | Low | P2 |
| ANSI color toggle | Low | Low | P3 |
| Debug messages | Low | Low | P3 |

### Verification Commands by Platform

**macOS:**
```bash
python3 --version
git --version
echo '{"model":{"display_name":"Test"}}' | python3 ~/.claude/statusline.py
```

**Linux:**
```bash
python3 --version
git --version
echo '{"model":{"display_name":"Test"}}' | python3 ~/.claude/statusline.py
```

**Windows (PowerShell):**
```powershell
python --version
git --version
echo '{"model":{"display_name":"Test"}}' | python "$env:USERPROFILE\.claude\statusline.py"
```

---

*Document generated by ps-analyst v2.0.0*
