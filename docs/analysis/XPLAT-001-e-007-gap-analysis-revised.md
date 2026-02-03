# Revised Cross-Platform Gap Analysis for jerry-statusline

**PS ID:** XPLAT-001
**Entry ID:** e-007
**Topic:** Revised Gap Analysis Addressing Adversarial Critique
**Date:** 2026-02-03
**Analyst:** ps-analyst v2.0.0
**Supersedes:** e-003

---

## REVISION SUMMARY

This document is a comprehensive revision of e-003 (original gap analysis) based on adversarial critique feedback from e-006. The critique identified significant blind spots and methodological issues.

### Key Changes from e-003

| Area | e-003 Status | e-007 Status | Change Type |
|------|-------------|--------------|-------------|
| Platform Scope | macOS, Windows, Linux (mainstream) | +Alpine, +Docker, +VS Code terminal, +SSH/tmux | **EXPANDED** |
| Risk Assessment | Medium for Windows | HIGH for Windows | **UPGRADED** |
| Evidence Type | Assumption-based | Verified vs Assumed matrix | **CLARIFIED** |
| Edge Cases | Minimal coverage | Comprehensive section | **ADDED** |
| Container Support | Not mentioned | Full analysis | **ADDED** |
| Effort Estimates | 13 hours | 35+ hours | **REVISED** |

### Critique Issues Addressed

| Critique ID | Issue | How Addressed |
|-------------|-------|---------------|
| CR-001 | Zero Windows testing | Documented as critical gap, not assumption |
| CR-002 | Zero Linux testing | Added container analysis |
| CR-004 | Alpine Linux excluded | Full musl libc analysis added |
| CR-005 | Container blindspot | Docker deployment section added |
| HR-001 | No locale testing | Non-UTF8 locale section added |
| HR-002 | Read-only filesystem silent failure | Detailed analysis added |
| MR-003 | UNC path handling | Windows network paths analyzed |

---

## L0 - Executive Summary (REVISED)

### Risk Level Upgrade Notice

**IMPORTANT:** The original analysis understated platform risks. This revision upgrades several risk assessments based on:
1. No empirical cross-platform testing has been performed
2. Docker/container environments were completely ignored
3. VS Code terminal (primary Claude Code environment) was not analyzed
4. Alpine Linux (most common Docker base) explicitly excluded by requirements

### Overall Risk Assessment (REVISED)

| Platform | e-003 Rating | e-007 Rating | Justification |
|----------|-------------|--------------|---------------|
| macOS | Low | **Low** | Development platform, well-tested |
| Linux (glibc) | Medium | **Medium-High** | No actual testing, documentation gap |
| Linux (Alpine/musl) | Not assessed | **HIGH** | Explicitly excluded, common in containers |
| Windows Native | Medium-High | **HIGH** | Zero testing, path edge cases |
| WSL 2 | Not assessed | **Medium** | Should work like Linux |
| Docker Container | Not assessed | **HIGH** | No TTY, git unavailable, read-only FS |
| VS Code Terminal | Not assessed | **Medium-High** | ANSI support varies |
| SSH/tmux Sessions | Not assessed | **Medium** | TERM variable issues |

### Deployment Risk Matrix

| Deployment Scenario | Risk | Recommended Action |
|--------------------|------|-------------------|
| macOS native terminal | LOW | Production ready |
| Ubuntu/Debian desktop | MEDIUM | Test before deployment |
| Windows Terminal | MEDIUM-HIGH | Test thoroughly |
| Windows cmd.exe | HIGH | Document as unsupported |
| Docker (Alpine base) | **CRITICAL** | Requires code changes |
| Docker (Debian base) | HIGH | Requires git installation |
| CI/CD environment | HIGH | Non-interactive mode needed |
| VS Code integrated terminal | MEDIUM-HIGH | Test ANSI rendering |
| SSH to remote server | MEDIUM | Test terminal passthrough |

---

## L1 - Gap Categories Analysis (REVISED)

### 1. Code Gaps

#### 1.1 Home Directory Expansion (REVISED)

**Current Implementation (lines 220, 234, 510):**
```python
state_file = Path(os.path.expanduser(config["compaction"]["state_file"]))
home = os.path.expanduser("~")
```

**Original Assessment:** LOW risk
**Revised Assessment:** **MEDIUM** risk

**Critique-Identified Issues:**

| Issue | Description | Evidence |
|-------|-------------|----------|
| `HOME` vs `USERPROFILE` | On Windows, `HOME` takes precedence over `USERPROFILE` | Python docs, NOT tested |
| Missing HOME variable | In containers, HOME may not be set | THEORETICAL |
| UNC paths | Network paths `\\server\share` may not expand correctly | UNTESTED |
| `Path.home()` vs `expanduser()` | These are NOT equivalent in edge cases | Code inspection |

**Code Analysis:**

The script uses BOTH `os.path.expanduser()` (lines 220, 234, 510) AND `Path.home()` (line 163):

```python
# Line 163 - Config loading
Path.home() / ".claude" / "ecw-statusline-config.json"

# Line 510 - Directory abbreviation
home = os.path.expanduser("~")
```

**Edge Case Behavior:**

| Scenario | `os.path.expanduser("~")` | `Path.home()` | Impact |
|----------|--------------------------|---------------|--------|
| `HOME` set, differs from actual home | Uses `HOME` | Uses pwd/registry | INCONSISTENT |
| `HOME` not set (container) | Falls back to `USERPROFILE` (Win) or `/etc/passwd` (Unix) | Same | OK |
| Neither `HOME` nor `USERPROFILE` set | Returns `~` unchanged | Raises `RuntimeError` | **CRASH** |
| UNC path in `USERPROFILE` | Unknown | Unknown | **UNTESTED** |

**Verified vs Assumed:**
- macOS behavior: ASSUMED (not tested empirically)
- Linux glibc behavior: ASSUMED (not tested empirically)
- Linux musl behavior: UNKNOWN
- Windows behavior: ASSUMED (not tested empirically)
- Container behavior: UNKNOWN

**Gap Status:** OPEN - Requires empirical testing

---

#### 1.2 Alpine Linux / musl libc Compatibility (NEW)

**Gap Type:** CRITICAL - Previously unidentified

**Background:**
The requirements document (e-002) specifies "Linux distributions with glibc 2.17+" but Alpine Linux, the default Docker base image, uses musl libc instead of glibc.

**Potential Differences:**

| Feature | glibc | musl | Impact |
|---------|-------|------|--------|
| `os.path.expanduser()` | Reads `/etc/passwd` | Same behavior expected | LOW |
| Subprocess timeout handling | Well-tested | Less tested | UNKNOWN |
| Unicode collation | Full ICU | Minimal | May affect git output sorting |
| Locale handling | Extensive | Minimal POSIX | **POTENTIAL ISSUE** |
| Signal handling | Standard | Subtle differences | UNKNOWN |

**Risk Assessment:**

| Aspect | Risk Level | Notes |
|--------|------------|-------|
| Core functionality | MEDIUM | May work but untested |
| Subprocess commands | MEDIUM | Timeout edge cases |
| Locale/encoding | HIGH | musl locale support limited |
| Error messages | LOW | May differ but functional |

**Evidence Level:** THEORETICAL - No actual Alpine Linux testing performed

**Current Behavior:** UNKNOWN - Script may work, fail silently, or crash

**Gap Status:** CRITICAL - Requires testing or explicit exclusion documentation

---

#### 1.3 Docker Container Environment (NEW)

**Gap Type:** HIGH - Previously unidentified

**Docker-Specific Issues:**

| Issue | Typical Docker State | Impact on Script | Code Location |
|-------|---------------------|------------------|---------------|
| No TTY | `os.get_terminal_size()` raises `OSError` | Falls back to 120 columns | Line 263-266 |
| No git | `FileNotFoundError` on subprocess | Git segment silently disappears | Lines 554-587 |
| Read-only filesystem | `IOError` on state file write | Compaction detection fails silently | Lines 236-241 |
| No HOME variable | `~` may not expand | Config/state files not found | Lines 163, 220 |
| Alpine base (musl) | Different C library | Unknown behavior | Throughout |

**Current Error Handling Analysis:**

```python
# Terminal size - Line 263-266 (ADEQUATE)
def get_terminal_width() -> int:
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 120  # Falls back gracefully

# Git commands - Lines 585-587 (SILENT FAILURE)
except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
    debug_log(f"Git error: {e}")
    return None  # User never knows why git segment is missing

# State file write - Lines 236-241 (SILENT FAILURE)
except IOError as e:
    debug_log(f"State save error: {e}")
    # Compaction detection silently disabled - user confused
```

**Container Deployment Scenarios:**

| Scenario | Works? | Issues |
|----------|--------|--------|
| Docker + Debian + git installed | Likely | Read-only FS issues |
| Docker + Alpine + git installed | Unknown | musl libc concerns |
| Docker + no git | Partial | Git segment missing |
| Docker + read-only rootfs | Partial | State persistence fails |
| Docker + no HOME set | Unknown | Config loading may fail |

**Evidence Level:** THEORETICAL - No Docker testing performed

**Gap Status:** HIGH - Requires container testing and documentation

---

#### 1.4 Read-Only Filesystem Handling (NEW)

**Gap Type:** HIGH - Silent failure identified

**Current Implementation (Lines 236-241):**
```python
def save_state(config: Dict, state: Dict[str, Any]) -> None:
    """Save current state for next invocation."""
    state_file = Path(os.path.expanduser(config["compaction"]["state_file"]))

    try:
        state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f)
    except IOError as e:
        debug_log(f"State save error: {e}")  # Silent failure!
```

**Impact Analysis:**

| Feature | Depends on State | Behavior on RO Filesystem |
|---------|------------------|--------------------------|
| Compaction detection | YES | Never shows compaction indicator |
| Session tracking | NO (from JSON input) | Works normally |
| All other segments | NO | Work normally |

**User Experience Problem:**
Users in read-only environments will:
1. Never see compaction indicators
2. Not know why (no error message to stdout)
3. Possibly file bug reports

**Proposed Solutions:**

| Solution | Effort | Impact |
|----------|--------|--------|
| Log warning to stderr | Low | User can see with `2>/dev/null` redirect |
| Config option for state file location | Medium | User can point to writable location |
| In-memory-only mode | Medium | Disable compaction detection gracefully |
| Document limitation | Low | At least users know |

**Evidence Level:** CODE INSPECTION - Verified via code analysis, not runtime testing

**Gap Status:** HIGH - Requires improved handling or documentation

---

#### 1.5 VS Code Integrated Terminal (NEW)

**Gap Type:** MEDIUM-HIGH - Primary execution environment not analyzed

**Background:**
Claude Code primarily runs inside VS Code's integrated terminal. This terminal has different ANSI handling than native terminals.

**Known VS Code Terminal Issues:**

| Issue | Description | Impact |
|-------|-------------|--------|
| 256-color support | Varies by VS Code version and settings | Colors may render incorrectly |
| Terminal.integrated.inheritEnv | May not inherit system TERM | Width detection affected |
| Windows VS Code + cmd.exe | Limited ANSI support | Colors may not work |
| Extension interference | Some extensions modify terminal | Unpredictable behavior |

**ANSI Support Matrix:**

| VS Code Version | Platform | 256-Color Support | Notes |
|-----------------|----------|-------------------|-------|
| 1.70+ | macOS | YES | Works well |
| 1.70+ | Linux | YES | Works well |
| 1.70+ | Windows (WT) | YES | Windows Terminal backend |
| 1.70+ | Windows (conhost) | LIMITED | May need VT mode enabled |
| < 1.60 | All | VARIES | Older versions less reliable |

**Current Code:**
```python
def ansi_color(code: int) -> str:
    """Generate ANSI 256-color escape sequence."""
    if code == 0:
        return "\033[0m"
    return f"\033[38;5;{code}m"
```

No capability detection, no fallback for terminals without 256-color support.

**Evidence Level:** DOCUMENTATION-BASED - Not empirically tested

**Gap Status:** MEDIUM-HIGH - Requires VS Code testing matrix

---

#### 1.6 SSH Sessions and tmux/screen (NEW)

**Gap Type:** MEDIUM - Previously unanalyzed

**TERM Variable Issues:**

| Scenario | Typical TERM | 256-Color? | Width Detection |
|----------|-------------|------------|-----------------|
| Direct terminal | `xterm-256color` | YES | Reliable |
| SSH (modern) | Inherited from client | Usually YES | Reliable |
| SSH (legacy) | `xterm` or `vt100` | NO | May fail |
| tmux | `screen-256color` | YES | Via TMUX_PANE |
| screen | `screen` | VARIES | May be cached |
| Nested tmux in SSH | Various | Complex | May be stale |

**Terminal Width Detection:**
```python
def get_terminal_width() -> int:
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 120
```

In SSH/tmux, this relies on the terminal emulator properly propagating SIGWINCH signals. May report stale values after resize.

**Evidence Level:** THEORETICAL - Based on known terminal behaviors

**Gap Status:** MEDIUM - Document recommendations for SSH/tmux users

---

#### 1.7 Non-UTF8 Locale Handling (NEW)

**Gap Type:** HIGH - Previously unanalyzed

**Current Code Patterns:**
```python
# File I/O - explicit UTF-8 (good)
with open(config_path, "r", encoding="utf-8") as f:
    user_config = json.load(f)

# Subprocess - text=True (uses system locale)
result = subprocess.run(
    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
    capture_output=True,
    text=True,  # Uses locale.getpreferredencoding()
    timeout=timeout,
)
```

**Issue:** `text=True` in subprocess uses the system's preferred encoding, NOT UTF-8. On systems with `LANG=C` or legacy Windows locales, this may fail.

**Scenarios:**

| LANG Value | Git Output Encoding | Subprocess Decoding | Result |
|------------|--------------------|--------------------|--------|
| `en_US.UTF-8` | UTF-8 | UTF-8 | OK |
| `C` or `POSIX` | ASCII (or system) | ASCII | May fail on non-ASCII branch names |
| `C.UTF-8` | UTF-8 | UTF-8 | OK |
| Windows legacy (cp1252) | System | System | Usually OK |
| Mixed encodings | ??? | ??? | **POTENTIAL FAILURE** |

**Emoji Handling:**

| Scenario | Behavior |
|----------|----------|
| UTF-8 terminal, `use_emoji: true` | Works |
| Non-UTF8 terminal, `use_emoji: true` | Mojibake or ? characters |
| Any terminal, `use_emoji: false` | Works (no emoji output) |

**Current Config Option:**
```python
"display": {
    "use_emoji": True,
}
```

Users CAN disable emoji, but many won't know they need to.

**Evidence Level:** CODE INSPECTION - Not tested with actual non-UTF8 locales

**Gap Status:** HIGH - Add encoding parameter to subprocess calls

---

#### 1.8 UNC Paths on Windows (NEW)

**Gap Type:** MEDIUM - Previously unanalyzed

**Background:**
Windows network paths use UNC format: `\\server\share\path`

**Potential Issues:**

| Operation | Code Location | UNC Behavior | Notes |
|-----------|---------------|--------------|-------|
| `os.path.expanduser("~")` | Lines 220, 510 | Returns local path | OK |
| `Path.home()` | Line 163 | Returns local path | OK |
| `subprocess cwd=...` | Lines 554, 571 | **UNKNOWN** | May fail |
| Path string operations | Line 511 | **May fail** | `startswith` comparison |

**Code Analysis:**
```python
# Line 510-512
home = os.path.expanduser("~")
if current_dir.startswith(home):  # What if current_dir is UNC?
    current_dir = "~" + current_dir[len(home):]
```

If `current_dir` is `\\server\share\project` and `home` is `C:\Users\user`, the `startswith` check correctly returns False. No crash, but no home abbreviation either.

**Subprocess with UNC cwd:**
```python
result = subprocess.run(
    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
    cwd=cwd,  # cwd might be UNC path
    ...
)
```

Python's subprocess on Windows can handle UNC paths for `cwd`, but:
1. Git behavior with UNC is less tested
2. Permission issues common on network drives
3. Network latency may cause timeout

**Evidence Level:** THEORETICAL - Not tested with actual UNC paths

**Gap Status:** MEDIUM - Document network drive limitations

---

### 2. Test Gaps (REVISED)

#### 2.1 Platform Test Execution Status (REVISED)

**CRITICAL: All platforms have ZERO actual test execution**

| Platform | Tests Written | Tests Executed | Evidence |
|----------|--------------|----------------|----------|
| macOS | 12+ | **0 verified** | Test suite runs but not in CI |
| Linux (glibc) | 0 | **0** | No Linux test runs |
| Linux (Alpine) | 0 | **0** | Not even considered |
| Windows | 0 | **0** | All "Pending" in V&V plan |
| Docker | 0 | **0** | Not considered |
| VS Code terminal | 0 | **0** | Not considered |

**Test Suite Analysis:**

The existing tests (`test_statusline.py`) use mocked payloads:
```python
PAYLOAD_NORMAL = {
    "cwd": "/home/user/ecw-statusline",  # Always Unix path
    ...
}
```

No Windows paths (`C:\Users\...`), no edge cases, no platform-specific assertions.

**Gap Status:** CRITICAL - CI/CD with multi-platform matrix required

---

#### 2.2 Missing Test Categories (EXPANDED)

| Test Category | Priority | Description | Effort |
|---------------|----------|-------------|--------|
| Windows path display | CRITICAL | `C:\Users\...` to `~\...` | 3h |
| Alpine Linux execution | CRITICAL | musl libc compatibility | 4h |
| Docker non-TTY | HIGH | `os.get_terminal_size()` fallback | 2h |
| Docker no git | HIGH | Graceful git segment omission | 2h |
| Read-only filesystem | HIGH | State file failure handling | 2h |
| VS Code terminal ANSI | HIGH | 256-color rendering | 2h |
| SSH terminal passthrough | MEDIUM | TERM variable handling | 2h |
| tmux/screen nested | MEDIUM | Terminal width detection | 1h |
| Non-UTF8 locale | HIGH | `LANG=C` subprocess handling | 2h |
| UNC paths | MEDIUM | Network drive handling | 2h |
| Missing HOME variable | HIGH | Container edge case | 1h |
| Git timeout on large repo | MEDIUM | 2s timeout adequacy | 1h |
| Unicode in paths | MEDIUM | CJK/emoji in usernames | 2h |

**Total Test Gap Effort:** ~26 hours

---

### 3. Documentation Gaps (REVISED)

#### 3.1 Linux Installation Documentation

**Original Status:** MISSING
**Revised Status:** STILL MISSING, expanded scope

**Required Sections:**

1. **Prerequisites**
   - Python 3.9+ installation (apt, dnf, pacman)
   - Git installation
   - Terminal requirements (256-color, emoji font)

2. **Distribution-Specific Instructions**
   - Ubuntu/Debian
   - Fedora/RHEL/CentOS
   - Arch Linux
   - Alpine Linux (if supported - currently NOT)

3. **Container Deployment**
   - Docker with Debian base
   - Docker with Alpine base (limitations)
   - Read-only filesystem workarounds
   - No-git deployment mode

4. **Terminal Emulator Recommendations**
   - GNOME Terminal
   - Konsole
   - Alacritty
   - kitty
   - xterm (limitations)

**Effort:** 4 hours

---

#### 3.2 Container Deployment Documentation (NEW)

**Status:** NOT EXISTS - Required

**Required Content:**

1. **Supported Base Images**
   - `python:3.9-slim` (Debian-based) - SUPPORTED
   - `python:3.9-alpine` - NOT SUPPORTED (musl libc)
   - `ubuntu:22.04` - SUPPORTED

2. **Installation in Dockerfile**
   ```dockerfile
   # Example for supported deployment
   FROM python:3.9-slim
   RUN apt-get update && apt-get install -y git
   COPY statusline.py /app/
   # Note: State file persistence requires volume mount
   ```

3. **Limitations**
   - No compaction detection without persistent state file
   - Git segment requires git binary
   - No terminal width detection (uses 120 default)
   - Read-only rootfs considerations

4. **CI/CD Usage**
   - Non-interactive mode
   - Headless execution
   - Piping considerations

**Effort:** 3 hours

---

#### 3.3 Platform Exclusions Documentation (NEW)

**Status:** NOT EXISTS - Required

**Must Explicitly State:**

| Platform | Support Status | Reason |
|----------|---------------|--------|
| Alpine Linux | NOT SUPPORTED | musl libc untested |
| FreeBSD | NOT SUPPORTED | Untested |
| Windows cmd.exe | NOT SUPPORTED | No ANSI 256-color |
| Windows PowerShell < 5.1 | NOT SUPPORTED | Limited ANSI |
| Python < 3.9 | NOT SUPPORTED | Type hints, features |
| Windows < 10 (1903) | NOT SUPPORTED | No VT100 mode |
| Termux (Android) | NOT SUPPORTED | Untested |
| ChromeOS (Crostini) | NOT SUPPORTED | Untested |

**Effort:** 1 hour

---

### 4. Edge Cases Section (NEW)

#### 4.1 Filesystem Edge Cases

| Edge Case | Current Behavior | Risk | Recommendation |
|-----------|------------------|------|----------------|
| Read-only filesystem | Silent state save failure | HIGH | Log warning, document |
| Full disk | Silent state save failure | MEDIUM | Catch OSError subtypes |
| Network home directory | Slow config/state access | MEDIUM | Document latency |
| Symlinked `~/.claude` | Should work (pathlib) | LOW | Test and document |
| Spaces in username | Should work | LOW | Test with `"John Doe"` |
| Unicode in username | Unknown on Windows | MEDIUM | Test CJK/emoji usernames |
| Very long paths | May exceed display | LOW | Truncation exists |

#### 4.2 Environment Edge Cases

| Edge Case | Current Behavior | Risk | Recommendation |
|-----------|------------------|------|----------------|
| `HOME` not set | `Path.home()` raises `RuntimeError` | HIGH | Add try/catch |
| `USERPROFILE` not set (Windows) | Falls back behavior | MEDIUM | Test and document |
| `LANG=C` | Subprocess may fail on non-ASCII | HIGH | Use `encoding='utf-8'` |
| `NO_COLOR` env var | Ignored | LOW | Consider implementing |
| `TERM=dumb` | Full output with ANSI codes | MEDIUM | Detect and strip |
| Container with no env | Multiple failures | HIGH | Document requirements |

#### 4.3 Git Edge Cases

| Edge Case | Current Behavior | Risk | Recommendation |
|-----------|------------------|------|----------------|
| Git not in PATH | Silent segment omission | MEDIUM | Document |
| Bare repository | `git status` may fail | LOW | Test |
| Detached HEAD | Shows commit hash | LOW | Already handles |
| Very long branch name | Truncated | LOW | Already handles |
| Large monorepo (>100k files) | May timeout | HIGH | Make timeout configurable |
| Shallow clone | May behave differently | LOW | Test |
| Worktrees | Should work | LOW | Test |
| Submodules | Should work | LOW | Test |
| Corrupted .git | Exception caught | LOW | Already handles |
| Git LFS enabled | May slow status | MEDIUM | Document |

---

## L2 - Verified vs Assumed Evidence Matrix (NEW)

### Legend
- **V** = Verified (empirically tested)
- **I** = Inspected (code review only)
- **D** = Documentation-based (Python/tool docs)
- **A** = Assumed (no evidence)
- **U** = Unknown (not analyzed)

### Core Functionality Matrix

| Feature | macOS | Linux (glibc) | Linux (musl) | Windows | Docker |
|---------|-------|---------------|--------------|---------|--------|
| Python execution | I | A | U | A | A |
| Config loading | I | A | U | A | A |
| JSON parsing | I | D | D | D | D |
| State persistence | I | A | U | A | U |
| ANSI color output | I | A | U | A | A |
| Terminal width | I | A | A | A | U |
| Emoji rendering | I | A | A | A | U |

### Path Handling Matrix

| Feature | macOS | Linux (glibc) | Linux (musl) | Windows | Docker |
|---------|-------|---------------|--------------|---------|--------|
| `os.path.expanduser("~")` | D | D | U | D | U |
| `Path.home()` | D | D | U | D | U |
| `Path` / operator | D | D | D | D | D |
| UNC paths | N/A | N/A | N/A | U | N/A |
| Unicode paths | A | A | U | U | U |

### Subprocess Matrix

| Feature | macOS | Linux (glibc) | Linux (musl) | Windows | Docker |
|---------|-------|---------------|--------------|---------|--------|
| Git execution | I | A | U | A | U |
| Timeout handling | I | A | U | D | A |
| Text encoding | D | D | U | A | U |
| Capture output | D | D | D | D | D |

### ANSI/Terminal Matrix

| Feature | macOS Term | Linux Term | VS Code | Windows Term | cmd.exe |
|---------|-----------|------------|---------|-------------|---------|
| 256-color | I | A | A | D | A |
| Reset sequences | I | A | A | D | A |
| Width detection | I | A | A | A | A |
| Emoji display | I | A | A | A | U |

---

## L3 - Prioritized Remediation Plan (REVISED)

### Critical Priority (Must address before production)

| ID | Gap | Remediation | Effort | e-003 Effort |
|----|-----|-------------|--------|--------------|
| G-001 | Alpine Linux/musl excluded | Document exclusion OR test and fix | 4h | Not identified |
| G-002 | Zero Windows testing | Create and run test matrix | 4h | Not identified |
| G-003 | Zero Linux testing | Create and run test matrix | 4h | Not identified |
| G-004 | No CI/CD pipeline | Create GitHub Actions workflow | 4h | 2h |
| G-005 | Container deployment blind spot | Test in Docker, document | 4h | Not identified |
| G-006 | Read-only filesystem silent failure | Add warning, document | 2h | Not identified |

**Critical Total:** 22 hours (vs e-003: 2 hours)

### High Priority (Address before GA)

| ID | Gap | Remediation | Effort | e-003 Effort |
|----|-----|-------------|--------|--------------|
| G-007 | Non-UTF8 locale handling | Add `encoding='utf-8'` to subprocess | 2h | Not identified |
| G-008 | VS Code terminal testing | Test ANSI rendering, document | 2h | Not identified |
| G-009 | Missing HOME handling | Add try/catch for `Path.home()` | 1h | Not identified |
| G-010 | Linux documentation | Write comprehensive guide | 4h | 2h |
| G-011 | Container documentation | Write deployment guide | 3h | Not identified |
| G-012 | Platform exclusions doc | Document unsupported platforms | 1h | Not identified |
| G-013 | Claude Code schema dependency | Add version check or documentation | 2h | Not identified |

**High Total:** 15 hours (vs e-003: 2 hours)

### Medium Priority (Address post-GA)

| ID | Gap | Remediation | Effort | e-003 Effort |
|----|-----|-------------|--------|--------------|
| G-014 | NO_COLOR env var support | Implement standard | 1h | Not identified |
| G-015 | UNC path documentation | Test and document Windows network | 2h | Not identified |
| G-016 | Large monorepo timeout | Make git timeout configurable | 1h | Not identified |
| G-017 | SSH/tmux documentation | Document terminal passthrough | 1h | Not identified |
| G-018 | WSL documentation | Clarify WSL vs native Windows | 1h | 1h |
| G-019 | ANSI color toggle | Add config to disable colors | 1h | 1h |

**Medium Total:** 7 hours (vs e-003: 2 hours)

### Low Priority (Nice to have)

| ID | Gap | Remediation | Effort | e-003 Effort |
|----|-----|-------------|--------|--------------|
| G-020 | ARM Linux testing | Test on Raspberry Pi | 2h | Not identified |
| G-021 | FreeBSD consideration | Test or document exclusion | 2h | Not identified |
| G-022 | Emoji ASCII fallback | Provide non-emoji alternatives | 1h | Not identified |
| G-023 | Upgrade path documentation | Document v2.0 to v2.1 migration | 1h | Not identified |

**Low Total:** 6 hours

---

## Summary Effort Comparison

| Priority | e-003 Estimate | e-007 Estimate | Difference |
|----------|---------------|----------------|------------|
| Critical | 0h (not identified) | 22h | +22h |
| High | 6h | 15h | +9h |
| Medium | 4h | 7h | +3h |
| Low | 3h | 6h | +3h |
| **Total** | **13h** | **50h** | **+37h** |

**Note:** The original 13-hour estimate was unrealistic because:
1. It assumed documentation-only fixes
2. It missed container/Docker scenarios entirely
3. It did not account for actual cross-platform testing effort
4. It understated the severity of untested code paths

---

## Appendix A: Code Line References (REVISED)

| Feature | Lines | Cross-Platform Risk |
|---------|-------|---------------------|
| Shebang | 1 | LOW (Windows ignores) |
| `from __future__ import annotations` | 37 | LOW (Python 3.9+ standard) |
| `pathlib.Path` imports | 44 | LOW (stdlib, tested) |
| Config path construction | 161-164 | MEDIUM (`Path.home()` edge cases) |
| State file loading | 218-229 | HIGH (expanduser, file access) |
| State file saving | 232-241 | HIGH (read-only FS silent fail) |
| ANSI color generation | 249-258 | MEDIUM (no capability detection) |
| Terminal width detection | 261-266 | LOW (graceful fallback) |
| Subprocess git calls | 553-587 | HIGH (encoding, timeout, availability) |
| Home abbreviation | 509-512 | MEDIUM (platform comparison) |

---

## Appendix B: Affected Requirements from e-002

| Requirement | Status After Critique | Notes |
|-------------|----------------------|-------|
| REQ-XPLAT-001.1 | Unverified | macOS not empirically tested |
| REQ-XPLAT-001.2 | **INVALID** | Excludes Alpine Linux (musl) |
| REQ-XPLAT-001.3 | Unverified | Windows not tested |
| REQ-XPLAT-002.1 | Verified (inspection) | Module list correct |
| REQ-XPLAT-003.1 | Unverified | macOS terminal not tested |
| REQ-XPLAT-003.3 | Unverified | Windows terminal not tested |
| REQ-XPLAT-003.x | **MISSING** | VS Code terminal not specified |
| REQ-XPLAT-010.x | Unverified | Error handling not tested |

---

## Appendix C: Adversarial Critique Traceability

| Critique Issue | Section Addressed | Resolution Status |
|----------------|-------------------|-------------------|
| Alpine Linux exclusion | 1.2 | DOCUMENTED |
| Docker container blind spot | 1.3 | DOCUMENTED |
| VS Code terminal | 1.5 | DOCUMENTED |
| SSH/tmux sessions | 1.6 | DOCUMENTED |
| Non-UTF8 locales | 1.7 | DOCUMENTED |
| Read-only filesystems | 1.4 | DOCUMENTED |
| UNC paths on Windows | 1.8 | DOCUMENTED |
| Verified vs Assumed gap | Section L2 | NEW MATRIX |
| Understated risk levels | Throughout | UPGRADED |
| Optimistic effort estimates | Section L3 | REVISED (13h -> 50h) |

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| e-003 | 2026-02-03 | ps-analyst v2.0.0 | Original gap analysis |
| e-007 | 2026-02-03 | ps-analyst v2.0.0 | Revised per adversarial critique |

**Supersedes:** XPLAT-001-e-003-gap-analysis.md

**Review Required By:** ps-critic v2.0.0

---

*Document generated by ps-analyst v2.0.0*
*"This revision addresses adversarial critique to provide a realistic assessment of cross-platform readiness."*
