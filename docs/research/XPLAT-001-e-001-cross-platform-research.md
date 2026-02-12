# Cross-Platform Compatibility Research for jerry-statusline

**PS ID:** XPLAT-001
**Entry ID:** e-001
**Topic:** Cross-Platform Compatibility Research
**Date:** 2026-02-03
**Status:** Complete

---

## L0: Executive Summary (Stakeholders)

### Overall Assessment: GOOD with Minor Adjustments Required

The `statusline.py` script (v2.1.0, 946 lines) is **well-positioned for cross-platform deployment** on macOS, Linux, and Windows. The codebase uses Python 3.9+ stdlib only with no external dependencies, which is ideal for portability.

### Key Findings

| Area | macOS | Linux | Windows | Risk Level |
|------|-------|-------|---------|------------|
| Path Handling | Full Support | Full Support | Full Support | LOW |
| Subprocess/Git | Full Support | Full Support | Requires PATH setup | MEDIUM |
| Terminal Colors | Full Support | Full Support | Conditional* | MEDIUM |
| Emoji Rendering | Full Support | Font-dependent | Terminal-dependent | LOW |
| File Encoding | UTF-8 default | UTF-8 default | Explicit UTF-8 needed | LOW |
| Shebang Line | Works | Works | Requires py.exe | LOW |

*Windows Terminal (default since Windows 11 22H2) provides full ANSI support; legacy CMD requires enablement.

### Recommended Actions

1. **No code changes required** for core functionality
2. **Documentation enhancement** needed for Windows installation
3. **Optional enhancement**: Add Windows ANSI enablement for legacy console users

### Business Impact

- **Time to cross-platform support**: Minimal (documentation only)
- **Risk of breaking changes**: Low
- **User experience parity**: Achievable with current architecture

---

## L1: Technical Findings (Engineers)

### 1. Path Handling Analysis

#### Current Implementation
```python
# Lines 161-164: Config path resolution
CONFIG_PATHS = [
    Path(__file__).parent / "ecw-statusline-config.json",
    Path.home() / ".claude" / "ecw-statusline-config.json",
]

# Line 220: State file path expansion
state_file = Path(os.path.expanduser(config["compaction"]["state_file"]))

# Lines 509-515: Home directory abbreviation
home = os.path.expanduser("~")
if current_dir.startswith(home):
    current_dir = "~" + current_dir[len(home):]
```

#### Platform Behavior

| Function | macOS/Linux | Windows |
|----------|-------------|---------|
| `Path.home()` | Returns `/Users/username` or `/home/username` | Returns `C:\Users\username` |
| `os.path.expanduser("~")` | Uses `$HOME` env var | Uses `%USERPROFILE%` (not `%HOME%` since Python 3.8) |
| `Path("/")` separator | Forward slash `/` | Backslash `\` (but `/` accepted) |

#### Compatibility Status: COMPATIBLE

The current code is **fully cross-platform compatible** because:
- `pathlib.Path` automatically uses the correct path separator
- `os.path.expanduser()` handles platform differences transparently
- `Path.home()` works identically across all platforms

**Sources:**
- [Python os.path.expanduser() documentation](https://docs.python.org/3/library/os.path.html)
- [Python pathlib documentation](https://docs.python.org/3/library/pathlib.html)
- [Cross-Platform Path Handling Guide](https://www.bomberbot.com/python/mastering-pythons-os-path-expanduser-a-comprehensive-guide-for-cross-platform-path-handling/)

---

### 2. Subprocess and Git Commands

#### Current Implementation
```python
# Lines 554-565: Git branch detection
result = subprocess.run(
    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
    cwd=cwd,
    capture_output=True,
    text=True,
    timeout=timeout,
)

# Lines 571-578: Git status check
result = subprocess.run(
    ["git", "status", "--porcelain"],
    cwd=cwd,
    capture_output=True,
    text=True,
    timeout=timeout,
)
```

#### Platform Behavior

| Aspect | macOS/Linux | Windows |
|--------|-------------|---------|
| `subprocess.run()` with list args | Uses `execvp()` | Uses `CreateProcess()` |
| `shell=False` (default) | Recommended, secure | Recommended, secure |
| Git executable name | `git` | `git.exe` (but `git` works if in PATH) |
| Git availability | Usually pre-installed (macOS) or via package manager | Requires Git for Windows installation |

#### Compatibility Status: COMPATIBLE (with prerequisite)

The current implementation is **correct and secure**:
- Uses `shell=False` (implicit default) - secure against injection
- Uses list arguments - correct for cross-platform
- Git commands (`rev-parse`, `status --porcelain`) are identical across platforms

**Windows Prerequisite:** Git for Windows must be installed and `git.exe` must be in PATH.

**Potential Issue:** On Windows, if Git is installed but not in PATH, the `FileNotFoundError` exception (line 585) will be caught gracefully, and git segment will be omitted.

**Sources:**
- [Python subprocess documentation](https://docs.python.org/3/library/subprocess.html)
- [Real Python subprocess guide](https://realpython.com/python-subprocess/)
- [Git for Windows PATH setup](https://www.delftstack.com/howto/git/add-git-to-path-on-windows/)

---

### 3. Terminal Operations and ANSI Colors

#### Current Implementation
```python
# Lines 249-258: ANSI color generation
def ansi_color(code: int) -> str:
    """Generate ANSI 256-color escape sequence."""
    if code == 0:
        return "\033[0m"
    return f"\033[38;5;{code}m"

def ansi_reset() -> str:
    """Generate ANSI reset escape sequence."""
    return "\033[0m"

# Lines 261-266: Terminal size detection
def get_terminal_width() -> int:
    """Get current terminal width."""
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 120
```

#### Platform Behavior: ANSI 256-Color Support

| Terminal | Platform | ANSI 256-Color Support |
|----------|----------|------------------------|
| Terminal.app | macOS | Full support |
| iTerm2 | macOS | Full support |
| gnome-terminal | Linux | Full support |
| Konsole | Linux | Full support |
| xterm | Linux/macOS | Full support |
| **Windows Terminal** | Windows 10/11 | **Full support** (default since Win11 22H2) |
| PowerShell 7+ | Windows | Full support (in Windows Terminal) |
| CMD.exe | Windows 10+ | Requires enablement* |
| Legacy conhost.exe | Windows | Requires enablement* |

*ANSI support in legacy Windows console requires Virtual Terminal Processing to be enabled.

#### Windows ANSI Enablement Methods

**Method 1: Registry (system-wide)**
```cmd
REG ADD HKCU\CONSOLE /f /v VirtualTerminalLevel /t REG_DWORD /d 1
```

**Method 2: Python runtime enablement**
```python
import os
os.system('')  # Simple trick that enables VT100 on Windows 10 1607+
```

**Method 3: ctypes API call**
```python
import ctypes
kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
```

#### Compatibility Status: MOSTLY COMPATIBLE

- **macOS/Linux**: Full support, no changes needed
- **Windows Terminal** (default in Win11): Full support, no changes needed
- **Legacy Windows console**: May require enablement

**Recommendation:** The script runs inside Claude Code's terminal, which likely uses a modern terminal emulator. No code changes recommended, but documentation should note Windows Terminal requirement.

**Sources:**
- [DEV.to: Enable ANSI escape sequences on Windows](https://dev.to/slendersnax/a-way-to-enable-ansi-escape-sequences-in-the-windows-virtual-terminal-using-python-32ok)
- [Python bug tracker: ANSI handling on Windows](https://bugs.python.org/issue40134)
- [SS64: ANSI colors in Windows CMD](https://ss64.com/nt/syntax-ansi.html)

---

### 4. Terminal Size Detection

#### Current Implementation
```python
def get_terminal_width() -> int:
    """Get current terminal width."""
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 120
```

#### Platform Behavior

| Aspect | macOS/Linux | Windows |
|--------|-------------|---------|
| `os.get_terminal_size()` | Full support | Full support |
| Piped output behavior | Raises `OSError` | Raises `OSError` |
| Default fallback needed | Yes | Yes |

#### Compatibility Status: FULLY COMPATIBLE

The current implementation is **ideal for cross-platform use**:
- Uses `os.get_terminal_size()` which is available on Unix and Windows (Python 3.3+)
- Correctly catches `OSError` for piped/redirected output
- Provides sensible fallback (120 columns)

**Note:** `shutil.get_terminal_size()` is the higher-level alternative that provides built-in fallback, but the current implementation is functionally equivalent.

**Sources:**
- [Python os.get_terminal_size() documentation](https://docs.python.org/3/library/os.html)
- [GeeksforGeeks: os.get_terminal_size()](https://www.geeksforgeeks.org/python/python-os-get_terminal_size-method/)

---

### 5. File I/O and Encoding

#### Current Implementation
```python
# Line 176: Config file reading
with open(config_path, "r", encoding="utf-8") as f:
    user_config = json.load(f)

# Lines 224-225: State file reading
with open(state_file, "r", encoding="utf-8") as f:
    return json.load(f)

# Lines 238-239: State file writing
with open(state_file, "w", encoding="utf-8") as f:
    json.dump(state, f)

# Line 314: Transcript file reading
with open(transcript_path, "r", encoding="utf-8") as f:
```

#### Platform Behavior

| Aspect | macOS/Linux | Windows |
|--------|-------------|---------|
| Default file encoding | UTF-8 | System locale (e.g., cp1252) |
| `encoding="utf-8"` explicit | Works | **Required for reliability** |
| JSON module | Platform-independent | Platform-independent |

#### Compatibility Status: FULLY COMPATIBLE

The current implementation is **exemplary for cross-platform file I/O**:
- **All file operations explicitly specify `encoding="utf-8"`** - this is critical for Windows compatibility
- JSON module itself is platform-independent
- No reliance on system default encoding

**Important Note:** Python 3.15 will make UTF-8 the default encoding on all platforms, but explicit specification remains best practice.

**Sources:**
- [PEP 686: Make UTF-8 mode default](https://peps.python.org/pep-0686/)
- [Python Friday: File Encodings Between Windows and Linux](https://improveandrepeat.com/2022/07/python-friday-130-different-file-encodings-between-windows-and-linux/)
- [DEV.to: Python UTF-8 mode on Windows](https://dev.to/methane/python-use-utf-8-mode-on-windows-212i)

---

### 6. Shebang Line Handling

#### Current Implementation
```python
#!/usr/bin/env python3
```

#### Platform Behavior

| Platform | Behavior |
|----------|----------|
| macOS/Linux | Kernel interprets shebang, finds `python3` via `env` |
| Windows | Shebang ignored by OS; Python Launcher (`py.exe`) interprets it |

#### Compatibility Status: FULLY COMPATIBLE

The current shebang is **optimal for cross-platform use**:
- `#!/usr/bin/env python3` is the recommended portable form
- Works on Unix systems via kernel shebang processing
- Works on Windows via Python Launcher for Windows (py.exe), installed with Python since 3.3
- The Python Launcher recognizes `/usr/bin/env` as a "virtual command" and searches PATH

**Windows Invocation:**
```cmd
py statusline.py          # Uses py.exe launcher
python statusline.py      # Direct python call
python3 statusline.py     # If python3.exe alias exists
```

**Line Ending Consideration:** Ensure files use LF (Unix) line endings, not CRLF. CRLF can cause `python3\r` interpreter errors on Unix.

**Sources:**
- [Python documentation: Using Python on Windows](https://docs.python.org/3/using/windows.html)
- [Real Python: Python Shebang](https://realpython.com/python-shebang/)
- [LWN.net: Shebang lines for Python on Windows](https://lwn.net/Articles/909410/)

---

### 7. Emoji Rendering

#### Current Implementation
```python
# Lines 672-673: Model icons
icons = {"opus": "\U0001F535", "sonnet": "\U0001F7E3", "haiku": "\U0001F7E2"}  # Blue, Purple, Green circles
icon = icons.get(tier, "\u26AA") if config["display"]["use_emoji"] else ""

# Various segment icons
icon = "\U0001F4CA " if config["display"]["use_emoji"] else ""  # Chart
icon = "\U0001F4B0 " if config["display"]["use_emoji"] else ""  # Money bag
icon = "\u26A1 " if config["display"]["use_emoji"] else ""      # Lightning
icon = "\u23F1\uFE0F " if config["display"]["use_emoji"] else ""  # Stopwatch
icon = "\U0001F4C9 " if config["display"]["use_emoji"] else ""  # Chart decreasing
icon = "\U0001F527 " if config["display"]["use_emoji"] else ""  # Wrench
icon = "\U0001F33F " if config["display"]["use_emoji"] else ""  # Herb (git branch)
icon = "\U0001F4C2 " if config["display"]["use_emoji"] else ""  # Folder
```

#### Platform Behavior

| Terminal | Platform | Emoji Support |
|----------|----------|---------------|
| Terminal.app | macOS | Full color emoji |
| iTerm2 | macOS | Full color emoji |
| gnome-terminal | Linux | Requires emoji font installed |
| Konsole | Linux | Requires emoji font installed |
| **Windows Terminal** | Windows | Full color emoji |
| CMD/PowerShell (legacy) | Windows | Limited/monochrome |

#### Compatibility Status: COMPATIBLE with graceful degradation

The current implementation is **well-designed**:
- Emoji can be disabled via `config["display"]["use_emoji"] = False`
- Non-emoji fallbacks are empty strings (segments remain functional)
- Users can configure based on their terminal capabilities

**Linux Font Requirement:** Users may need to install emoji fonts:
```bash
# Debian/Ubuntu
sudo apt install fonts-noto-color-emoji

# Fedora
sudo dnf install google-noto-emoji-fonts
```

**Sources:**
- [GitHub: Windows Terminal emoji issues](https://github.com/microsoft/terminal/issues/16852)
- [DEV.to: Fixing emoji support in Linux terminal](https://dev.to/thiagomg/fixing-emoji-support-in-the-linux-terminal-34og)
- [Arch Linux Forums: Emoji display issues](https://bbs.archlinux.org/viewtopic.php?id=265119)

---

### 8. Environment Variables

#### Current Implementation
```python
# Line 209: Debug mode check
if os.environ.get("ECW_DEBUG") == "1":
    print(f"[ECW-DEBUG] {message}", file=sys.stderr)
```

#### Platform Behavior

| Aspect | macOS/Linux | Windows |
|--------|-------------|---------|
| `os.environ.get()` | Works | Works |
| Environment variable syntax | `export VAR=value` | `set VAR=value` (CMD) or `$env:VAR="value"` (PowerShell) |
| Case sensitivity | Case-sensitive | Case-insensitive |

#### Compatibility Status: FULLY COMPATIBLE

The `os.environ.get()` API is platform-independent. The only difference is how users set the variable:

```bash
# macOS/Linux
export ECW_DEBUG=1

# Windows CMD
set ECW_DEBUG=1

# Windows PowerShell
$env:ECW_DEBUG="1"
```

---

## L2: Strategic Implications (Architects)

### Architecture Assessment

The `statusline.py` architecture is **fundamentally sound for cross-platform deployment**:

1. **Single-file deployment**: Eliminates dependency management complexity
2. **Stdlib-only**: No pip install required, reducing platform-specific package issues
3. **Explicit encoding**: Future-proof against Python encoding changes
4. **Graceful degradation**: Git segment omits cleanly if git unavailable
5. **Configurable display**: Emoji toggle allows adaptation to terminal capabilities

### Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Git not in PATH (Windows) | Medium | Low | Git segment gracefully omits |
| ANSI colors not rendered (legacy Windows) | Low | Medium | Windows Terminal is now default |
| Emoji rendering issues | Low | Low | Configurable `use_emoji` setting |
| File encoding issues | Very Low | Medium | Already mitigated with explicit UTF-8 |
| Shebang not working | Low | Low | Python Launcher handles this |

### Recommended Documentation Additions

#### Windows Installation Guide

```markdown
## Windows Installation

### Prerequisites
1. Python 3.9+ installed (includes py.exe launcher)
2. Git for Windows installed and in PATH (optional, for git segment)
3. Windows Terminal (recommended) or Windows 10 1607+ with ANSI enabled

### Installation Steps
1. Copy `statusline.py` to `%USERPROFILE%\.claude\statusline.py`
2. Add to `%USERPROFILE%\.claude\settings.json`:
   ```json
   {
     "statusLine": {
       "type": "command",
       "command": "py %USERPROFILE%\\.claude\\statusline.py",
       "padding": 0
     }
   }
   ```

### Troubleshooting
- **No colors?** Ensure you're using Windows Terminal or enable VT processing
- **No git info?** Verify `git --version` works in your terminal
- **Emoji issues?** Set `"use_emoji": false` in config file
```

### Future Enhancement Opportunities

1. **Auto-detect Windows ANSI support**: Could add runtime detection and enablement
2. **Platform-specific config defaults**: Could adjust defaults based on `sys.platform`
3. **Emoji fallback characters**: Could use ASCII alternatives instead of empty strings

### Conclusion

The jerry-statusline codebase demonstrates **mature cross-platform design patterns**. No code changes are required for cross-platform compatibility. The recommended action is to enhance documentation with Windows-specific installation instructions.

---

## References

### Python Documentation
- [os.path.expanduser()](https://docs.python.org/3/library/os.path.html)
- [pathlib](https://docs.python.org/3/library/pathlib.html)
- [subprocess](https://docs.python.org/3/library/subprocess.html)
- [Using Python on Windows](https://docs.python.org/3/using/windows.html)

### Cross-Platform Guides
- [Bomberbot: Cross-Platform Path Handling](https://www.bomberbot.com/python/mastering-pythons-os-path-expanduser-a-comprehensive-guide-for-cross-platform-path-handling/)
- [Real Python: subprocess](https://realpython.com/python-subprocess/)
- [Real Python: Python Shebang](https://realpython.com/python-shebang/)

### Windows-Specific
- [DEV.to: ANSI Escape Sequences on Windows](https://dev.to/slendersnax/a-way-to-enable-ansi-escape-sequences-in-the-windows-virtual-terminal-using-python-32ok)
- [PEP 686: UTF-8 Mode Default](https://peps.python.org/pep-0686/)
- [Git for Windows PATH Setup](https://www.delftstack.com/howto/git/add-git-to-path-on-windows/)

### Terminal and Emoji
- [GitHub: Windows Terminal Issues](https://github.com/microsoft/terminal/issues/16852)
- [DEV.to: Linux Terminal Emoji Support](https://dev.to/thiagomg/fixing-emoji-support-in-the-linux-terminal-34og)
- [GeeksforGeeks: os.get_terminal_size()](https://www.geeksforgeeks.org/python/python-os-get_terminal_size-method/)
