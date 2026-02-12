# Getting Started with ECW Status Line

A step-by-step guide to installing and configuring ECW Status Line for Claude Code.

**Primary Platform:** macOS with zsh
**Also Supported:** Windows 10/11 with PowerShell, Linux (Ubuntu/Debian, Fedora/RHEL)

---

## Table of Contents

1. [Supported Platforms](#supported-platforms)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Verification](#verification)
5. [Configuration](#configuration)
6. [Enabling the Tools Segment](#enabling-the-tools-segment)
7. [Customization Examples](#customization-examples)
8. [Advanced Configuration](#advanced-configuration)
9. [Docker and Containers](#docker-and-containers)
10. [Windows UNC Paths](#windows-unc-paths)
11. [SSH and tmux](#ssh-and-tmux)
12. [Troubleshooting](#troubleshooting)
13. [Uninstallation](#uninstallation)

---

## Supported Platforms

| Platform | Status | Notes |
|----------|--------|-------|
| macOS 12+ (Intel & Apple Silicon) | **Fully Supported** | Primary development platform |
| Windows 10/11 (PowerShell) | **Fully Supported** | Windows Terminal recommended |
| Ubuntu 22.04+ / Debian 12+ | **Fully Supported** | CI-tested |
| Fedora 38+ / RHEL 9+ | **Supported** | Same as Ubuntu instructions |
| WSL 2 (Windows Subsystem for Linux) | **Supported** | Follow Linux instructions |
| Docker containers (glibc-based) | **Supported** | Gracefully handles missing HOME, read-only FS |
| Alpine Linux / musl-based | **Not Tested** | May work (stdlib only) but not validated. Prefer glibc-based images |
| FreeBSD | **Not Tested** | May work but not validated |
| ARM Linux (Raspberry Pi) | **Not Tested** | Python stdlib-only, should work but not validated |

> **Note:** Alpine Linux uses musl libc and has not been tested. The script is stdlib-only so it may work,
> but for guaranteed compatibility use `python:3.11-slim` (Debian-based) instead of `python:3.11-alpine`.

---

## Prerequisites

### macOS

#### 1. Python 3.9 or later

Check your Python version:

```bash
python3 --version
```

**Expected output:**
```
Python 3.9.x  (or higher, e.g., 3.10.x, 3.11.x, 3.12.x)
```

If Python is not installed or version is below 3.9:

```bash
# Install via Homebrew (recommended)
brew install python@3.11

# Verify installation
python3 --version
```

<details>
<summary>Don't have Homebrew?</summary>

Install Homebrew first:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then install Python:
```bash
brew install python@3.11
```
</details>

#### 2. Claude Code CLI

Verify Claude Code is installed:

```bash
claude --version
```

**Expected output:**
```
claude-code version X.X.X
```

If not installed, follow [Claude Code installation instructions](https://docs.anthropic.com/claude-code/getting-started).

#### 3. Git (Optional, for git segment)

```bash
git --version
```

**Expected output:**
```
git version 2.x.x
```

#### 4. Terminal with emoji support

macOS Terminal.app and iTerm2 both support emoji by default. No action needed.

To verify, run:
```bash
echo "🟣 📊 💰 ⚡ ⏱️ 🔧 🌿 📂"
```

You should see 8 distinct emoji icons.

---

### Windows

#### 1. Python 3.9 or later

Open PowerShell and check:

```powershell
python --version
```

**Expected output:**
```
Python 3.9.x  (or higher)
```

If Python is not installed:

1. Download from [python.org](https://www.python.org/downloads/windows/)
2. Run installer, **check "Add Python to PATH"**
3. Restart PowerShell
4. Verify: `python --version`

#### 2. Claude Code CLI

```powershell
claude --version
```

If not installed, follow [Claude Code installation instructions](https://docs.anthropic.com/claude-code/getting-started).

#### 3. Windows Terminal (Recommended)

For best emoji and color support, use [Windows Terminal](https://aka.ms/terminal) instead of the default Command Prompt.

#### WSL vs Native Windows

| Scenario | Recommendation |
|----------|---------------|
| Claude Code runs in PowerShell | Use **native Windows** instructions above |
| Claude Code runs in WSL 2 | Use **Linux** instructions below |
| Using VS Code + WSL remote | Use **Linux** instructions (VS Code forwards to WSL) |

> **Tip:** If you use WSL 2, install ECW Status Line inside the WSL filesystem (`~/.claude/`), not on the Windows side. The script and Claude Code should both run in the same environment.

#### 4. Git (Optional)

```powershell
git --version
```

If not installed, download from [git-scm.com](https://git-scm.com/download/win).

---

### Linux (Ubuntu/Debian)

#### 1. Python 3.9 or later

```bash
python3 --version
```

If Python is not installed or version is below 3.9:

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y python3 python3-pip

# Fedora/RHEL
sudo dnf install -y python3

# Verify
python3 --version
```

#### 2. Claude Code CLI

```bash
claude --version
```

If not installed, follow [Claude Code installation instructions](https://docs.anthropic.com/claude-code/getting-started).

#### 3. Git (Optional)

```bash
# Ubuntu/Debian
sudo apt install -y git

# Fedora/RHEL
sudo dnf install -y git
```

#### 4. Terminal with emoji support

Most modern Linux terminal emulators (GNOME Terminal, Konsole, Alacritty, kitty) support emoji. If your terminal does not, disable emoji:

```json
{
  "display": {
    "use_emoji": false
  }
}
```

---

## Installation

### macOS

#### Step 1: Create the Claude configuration directory (if it doesn't exist)

```bash
mkdir -p ~/.claude
```

#### Step 2: Download the status line script

```bash
curl -o ~/.claude/statusline.py https://raw.githubusercontent.com/geekatron/ecw-statusline/main/statusline.py
```

**Expected output:**
```
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 26692  100 26692    0     0  xxxxx      0 --:--:-- --:--:-- --:--:-- xxxxx
```

#### Step 3: Make the script executable

```bash
chmod +x ~/.claude/statusline.py
```

#### Step 4: Verify the script runs

```bash
echo '{"model":{"display_name":"Test"}}' | python3 ~/.claude/statusline.py
```

**Expected output:**
```
🟣 Test | 📊 ~[░░░░░░░░░░] 0% | 💰 $0.00 | ⚡ 0→ 0↺ | ⏱️ 0m 0tok | 📂 ~
```

If you see colored output with emoji, the script is working correctly.

#### Step 5: Configure Claude Code

Check if settings.json exists:

```bash
cat ~/.claude/settings.json 2>/dev/null || echo "File does not exist"
```

**If file does not exist**, create it:

```bash
cat > ~/.claude/settings.json << 'EOF'
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/statusline.py",
    "padding": 0
  }
}
EOF
```

**If file already exists**, you need to add the statusLine configuration. Open the file:

```bash
open -e ~/.claude/settings.json
```

Add the `statusLine` section (merge with existing content):

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/statusline.py",
    "padding": 0
  }
}
```

#### Step 6: Restart Claude Code

If Claude Code is running, restart it to load the new status line:

```bash
# Exit current session (type in Claude Code)
/exit

# Start new session
claude
```

---

### Windows

#### Step 1: Create the Claude configuration directory

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude"
```

#### Step 2: Download the status line script

```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/geekatron/ecw-statusline/main/statusline.py" -OutFile "$env:USERPROFILE\.claude\statusline.py"
```

#### Step 3: Verify the script runs

```powershell
echo '{"model":{"display_name":"Test"}}' | python "$env:USERPROFILE\.claude\statusline.py"
```

**Expected output:**
```
🟣 Test | 📊 ~[░░░░░░░░░░] 0% | 💰 $0.00 | ⚡ 0→ 0↺ | ⏱️ 0m 0tok | 📂 ~
```

#### Step 4: Configure Claude Code

Check if settings.json exists:

```powershell
Test-Path "$env:USERPROFILE\.claude\settings.json"
```

**If False**, create it:

```powershell
@"
{
  "statusLine": {
    "type": "command",
    "command": "python %USERPROFILE%\\.claude\\statusline.py",
    "padding": 0
  }
}
"@ | Out-File -FilePath "$env:USERPROFILE\.claude\settings.json" -Encoding utf8
```

**If True**, open and edit manually:

```powershell
notepad "$env:USERPROFILE\.claude\settings.json"
```

Add the `statusLine` section.

#### Step 5: Restart Claude Code

Exit and restart Claude Code to load the new status line.

---

### Linux

#### Step 1: Create the Claude configuration directory

```bash
mkdir -p ~/.claude
```

#### Step 2: Download the status line script

```bash
curl -o ~/.claude/statusline.py https://raw.githubusercontent.com/geekatron/ecw-statusline/main/statusline.py
```

#### Step 3: Make the script executable

```bash
chmod +x ~/.claude/statusline.py
```

#### Step 4: Verify the script runs

```bash
echo '{"model":{"display_name":"Test"}}' | python3 ~/.claude/statusline.py
```

You should see colored output with segment data.

#### Step 5: Configure Claude Code

```bash
# Create settings.json if it doesn't exist
cat > ~/.claude/settings.json << 'EOF'
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/statusline.py",
    "padding": 0
  }
}
EOF
```

If `~/.claude/settings.json` already exists, add the `statusLine` section to the existing JSON.

#### Step 6: Restart Claude Code

```bash
/exit
claude
```

---

## Verification

After installation, start Claude Code and verify the status line appears at the bottom of your terminal.

### What you should see

```
🟣 Sonnet | 📊 [░░░░░░░░░░] 0% | 💰 $0.00 | ⚡ 0→ 0↺ | ⏱️ 0m 0tok | 🌿 main ✓ | 📂 ~/your-project
```

### Segment breakdown

| Segment | What it shows | Your value |
|---------|---------------|------------|
| 🟣 Sonnet | Active model | Should match your current model |
| 📊 [░░░░░░░░░░] 0% | Context window usage | Starts at 0%, increases as you chat |
| 💰 $0.00 | Session cost | Starts at $0.00, increases with usage |
| ⚡ 0→ 0↺ | Token breakdown (fresh→ cached↺) | Shows fresh vs cached input tokens |
| ⏱️ 0m 0tok | Session duration + total tokens | Time since session started |
| 🌿 main ✓ | Git branch + status | Your current branch, ✓=clean ●=dirty |
| 📂 ~/your-project | Working directory | Your current directory |

### Verification checklist

- [ ] Status line appears at bottom of terminal
- [ ] Model name is displayed correctly
- [ ] Emoji icons render properly (not boxes or question marks)
- [ ] Colors are visible (green, yellow indicators)
- [ ] Git branch shows correctly (if in a git repo)
- [ ] Status updates after sending a message to Claude

---

## Configuration

ECW Status Line works out-of-the-box with sensible defaults. Configuration is optional.

### Creating a configuration file

#### macOS

```bash
cat > ~/.claude/ecw-statusline-config.json << 'EOF'
{
  "context": {
    "warning_threshold": 0.65,
    "critical_threshold": 0.85
  },
  "cost": {
    "green_max": 1.00,
    "yellow_max": 5.00
  }
}
EOF
```

#### Windows

```powershell
@"
{
  "context": {
    "warning_threshold": 0.65,
    "critical_threshold": 0.85
  },
  "cost": {
    "green_max": 1.00,
    "yellow_max": 5.00
  }
}
"@ | Out-File -FilePath "$env:USERPROFILE\.claude\ecw-statusline-config.json" -Encoding utf8
```

### Configuration options

You only need to specify values you want to change. All other settings use defaults.

| Setting | Default | Description |
|---------|---------|-------------|
| `context.warning_threshold` | 0.65 | Context % for yellow warning |
| `context.critical_threshold` | 0.85 | Context % for red warning |
| `cost.green_max` | 1.00 | Max cost ($) for green |
| `cost.yellow_max` | 5.00 | Max cost ($) for yellow |
| `display.compact_mode` | false | Show fewer segments |
| `display.use_emoji` | true | Use emoji icons |
| `display.use_color` | true | Enable/disable ANSI color codes |
| `tools.enabled` | false | Show tools segment |
| `advanced.git_timeout` | 2 | Git command timeout in seconds |

See [README.md](README.md) for complete configuration reference.

---

## Enabling the Tools Segment

The tools segment shows which Claude Code tools are consuming the most tokens:

```
🔧 Read:2.1k Edit:1.5k Bash:500
```

### To enable

#### macOS

```bash
cat > ~/.claude/ecw-statusline-config.json << 'EOF'
{
  "tools": {
    "enabled": true,
    "top_n": 3,
    "min_tokens": 100
  }
}
EOF
```

#### Windows

```powershell
@"
{
  "tools": {
    "enabled": true,
    "top_n": 3,
    "min_tokens": 100
  }
}
"@ | Out-File -FilePath "$env:USERPROFILE\.claude\ecw-statusline-config.json" -Encoding utf8
```

### Tools segment options

| Option | Default | Description |
|--------|---------|-------------|
| `enabled` | false | Enable/disable tools segment |
| `top_n` | 3 | Number of top tools to show |
| `min_tokens` | 100 | Minimum tokens for tool to appear |
| `cache_ttl_seconds` | 5 | Cache duration for transcript parsing |

---

## Customization Examples

### Example 1: Compact mode for small terminals

```json
{
  "display": {
    "compact_mode": true
  }
}
```

**Result:**
```
🟣 Sonnet | 📊 [▓▓▓▓░░░░░░] 42% | 💰 $1.23 | 🌿 main ✓
```

### Example 2: Higher cost thresholds for heavy usage

```json
{
  "cost": {
    "green_max": 5.00,
    "yellow_max": 20.00
  }
}
```

### Example 3: Disable emoji for minimal terminals

```json
{
  "display": {
    "use_emoji": false
  }
}
```

**Result:**
```
Sonnet | [▓▓▓▓░░░░░░] 42% | $1.23 | 78% | 2h12m | main ✓ | ~/project
```

### Example 4: Only show model, context, and cost

```json
{
  "segments": {
    "tokens": false,
    "session": false,
    "git": false,
    "directory": false
  }
}
```

**Result:**
```
🟣 Sonnet | 📊 [▓▓▓▓░░░░░░] 42% | 💰 $1.23
```

### Example 5: Full featured with tools

```json
{
  "tools": {
    "enabled": true,
    "top_n": 3
  },
  "context": {
    "warning_threshold": 0.50
  }
}
```

---

## Advanced Configuration

### Git Timeout

For large monorepos where git operations may be slow, increase the git timeout (default: 2 seconds):

```json
{
  "advanced": {
    "git_timeout": 5
  }
}
```

If your repository is very large and git operations still time out, you can disable the git segment entirely:

```json
{
  "segments": {
    "git": false
  }
}
```

### Color Control

#### Disabling Colors via Configuration

To disable all ANSI color codes (useful for terminals without color support):

```json
{
  "display": {
    "use_color": false
  }
}
```

This produces plain text output without any ANSI escape sequences. Emoji icons are still shown unless separately disabled with `"use_emoji": false`.

#### NO_COLOR Environment Variable

ECW Status Line respects the [NO_COLOR](https://no-color.org/) standard. When the `NO_COLOR` environment variable is set (to any value), all ANSI color codes are suppressed:

```bash
export NO_COLOR=1
```

**Precedence:** `NO_COLOR` environment variable takes absolute precedence over the `use_color` configuration option. When `NO_COLOR` is set, colors are always disabled regardless of config.

| NO_COLOR | use_color | Result |
|----------|-----------|--------|
| Not set | true (default) | Colors enabled |
| Not set | false | Colors disabled |
| Set | true | Colors disabled (NO_COLOR wins) |
| Set | false | Colors disabled |

---

## Claude Code JSON Schema

ECW Status Line reads its input from stdin as a JSON object provided by Claude Code's `statusLine` hook. The schema is **not formally documented** by Anthropic and may change between Claude Code versions.

### Expected Input Fields

```json
{
  "hook_event_name": "Status",
  "session_id": "string",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/current/working/directory",
  "version": "1.0.80",
  "model": {
    "id": "claude-sonnet-4-20250514",
    "display_name": "Sonnet"
  },
  "workspace": {
    "current_dir": "/path/to/project",
    "project_dir": "/path/to/project"
  },
  "cost": {
    "total_cost_usd": 0.45,
    "total_duration_ms": 300000,
    "total_lines_added": 156,
    "total_lines_removed": 23
  },
  "context_window": {
    "total_input_tokens": 15234,
    "total_output_tokens": 9412,
    "context_window_size": 200000,
    "current_usage": {
      "input_tokens": 8500,
      "output_tokens": 1200,
      "cache_creation_input_tokens": 5000,
      "cache_read_input_tokens": 12000
    }
  }
}
```

### Schema Stability

| Field | Stability | Notes |
|-------|-----------|-------|
| `model.id`, `model.display_name` | Stable | Core model identification |
| `context_window.context_window_size` | Stable | Window size |
| `context_window.current_usage.*` | Semi-stable | Token breakdown fields |
| `cost.total_cost_usd` | Stable | Session cost |
| `cost.total_duration_ms` | Stable | Session duration |
| `transcript_path` | Semi-stable | Path to JSONL transcript |
| `workspace.current_dir` | Stable | Working directory |

> **Note:** ECW Status Line uses `safe_get()` for all field access, so missing or renamed fields will not crash the script. If Claude Code changes the schema, affected segments will show default values (0, empty string) rather than errors.

---

## Docker and Containers

ECW Status Line is hardened for container environments where `HOME` may not be set, the filesystem may be read-only, or no TTY is available.

### Supported base images

| Image | Status | Notes |
|-------|--------|-------|
| `python:3.11-slim` | Recommended | Debian-based, small footprint |
| `python:3.11` | Supported | Full Debian image |
| `ubuntu:22.04` | Supported | Install python3 separately |
| `python:3.11-alpine` | **Not Tested** | musl libc; may work but not validated |

### Container behavior

When running in a container:

- **Missing HOME**: The script skips `~/.claude/` config paths and state file writes. No crash.
- **Read-only filesystem**: State file writes fail gracefully with a debug log message. Output is still produced.
- **No TTY**: Output works via pipe (stdin/stdout) without a terminal attached.

### Example Dockerfile

```dockerfile
FROM python:3.11-slim
COPY statusline.py /opt/statusline.py
# No additional dependencies needed (stdlib only)
CMD ["python3", "/opt/statusline.py"]
```

### Testing container behavior locally

```bash
# Test without HOME set
unset HOME && echo '{"model":{"display_name":"Test"}}' | python3 statusline.py

# Test with read-only state path (uses debug mode)
ECW_DEBUG=1 echo '{"model":{"display_name":"Test"}}' | python3 statusline.py
```

---

## VS Code Integrated Terminal

ECW Status Line works in the VS Code integrated terminal. VS Code's terminal uses `xterm-256color` and supports ANSI escape sequences and Unicode/emoji.

> **Note:** VS Code compatibility is based on documented terminal capabilities (`xterm-256color`, ANSI support). Empirical testing across macOS/Windows/Linux VS Code environments has not yet been performed. Please report any display issues via GitHub Issues.

### Setup

No special configuration is needed. If you run Claude Code inside VS Code's terminal, the status line will display correctly.

### Known Considerations

| Item | Details |
|------|---------|
| ANSI colors | Fully supported (256-color mode) |
| Emoji rendering | Supported in VS Code 1.70+ with a font that includes emoji glyphs |
| Terminal width | VS Code terminal panels can be narrow; `auto_compact_width: 80` triggers compact mode automatically |
| WSL Remote | If using VS Code + WSL Remote, the terminal runs inside WSL; use Linux installation instructions |
| Font recommendation | Use a Nerd Font or font with emoji support (e.g., "Cascadia Code", "FiraCode Nerd Font") |

### Disabling Emoji for VS Code

If your VS Code font does not render emoji correctly, disable them:

```json
{
  "display": {
    "use_emoji": false
  }
}
```

This replaces all emoji and Unicode special characters with ASCII equivalents.

---

## Windows UNC Paths

### Known Limitations

UNC paths (`\\server\share\path`) are **not officially supported** by ECW Status Line. The script uses `pathlib.Path` internally, which handles UNC paths inconsistently across Python versions and Windows configurations.

### Symptoms

If your Claude Code working directory uses a UNC path, you may see:
- Incorrect directory display in the status line
- Git segment not appearing (git may not resolve the repo)
- State file not saved (path resolution failure)

### Recommendations

| Scenario | Solution |
|----------|----------|
| Network drive | Map to a drive letter (e.g., `Z:\`) instead of using `\\server\share` |
| WSL | Use Linux paths inside WSL (e.g., `/home/user/project`) |
| Mounted share | Use the mount point path, not the UNC path |

> **Note:** This limitation applies only to the working directory path displayed by Claude Code. The script itself should be installed locally (`~/.claude/statusline.py`), not on a network share.

---

## SSH and tmux

> **Note:** SSH and tmux guidance below is based on standard terminal capabilities and common configurations. Empirical testing across all SSH client/server combinations and tmux versions has not been performed. Please report any issues via GitHub Issues.

### SSH Remote Sessions

ECW Status Line works in SSH sessions with the following requirements:

| Requirement | Details |
|-------------|---------|
| TERM variable | Must be set to a value supporting ANSI (e.g., `xterm-256color`) |
| Python 3.9+ | Must be installed on the remote host |
| Claude Code | Must be running on the remote host |

**Common SSH issues:**

```bash
# If TERM is not set correctly over SSH:
export TERM=xterm-256color

# If colors don't work, try:
echo $TERM  # Should be xterm-256color or similar

# If emoji don't render over SSH, disable them:
# Add to ecw-statusline-config.json:
# {"display": {"use_emoji": false}}
```

### tmux Sessions

ECW Status Line works inside tmux with proper configuration:

```bash
# Ensure tmux uses 256 colors
# Add to ~/.tmux.conf:
set -g default-terminal "screen-256color"

# Or start tmux with:
tmux -2  # Forces 256 color mode
```

| Issue | Solution |
|-------|----------|
| No colors in tmux | Add `set -g default-terminal "screen-256color"` to `~/.tmux.conf` |
| Garbled emoji in tmux | Use `tmux -2` flag or disable emoji via config |
| Status line not updating | Ensure Claude Code's status hook runs in the tmux pane |

> **Tip:** If you use both SSH and tmux (SSH into a server, then attach tmux), ensure TERM is set correctly in BOTH the SSH connection and the tmux session.

---

## Troubleshooting

### Status line not appearing

**Symptom:** Claude Code runs but no status line shows.

**Solutions:**

1. **Verify settings.json syntax:**
   ```bash
   # macOS
   python3 -m json.tool ~/.claude/settings.json

   # Windows
   python -m json.tool "$env:USERPROFILE\.claude\settings.json"
   ```

   If you see an error, fix the JSON syntax.

2. **Check script path:**
   ```bash
   # macOS
   ls -la ~/.claude/statusline.py

   # Windows
   dir "$env:USERPROFILE\.claude\statusline.py"
   ```

   File should exist and be readable.

3. **Test script directly:**
   ```bash
   echo '{"model":{"display_name":"Test"}}' | python3 ~/.claude/statusline.py
   ```

   Should produce output without errors.

4. **Restart Claude Code** after making changes.

### Emoji showing as boxes or question marks

**Symptom:** Seeing `□` or `?` instead of emoji.

**Solutions:**

1. **macOS Terminal.app:** Should work by default. Try iTerm2 if issues persist.

2. **Windows:** Use [Windows Terminal](https://aka.ms/terminal) instead of Command Prompt.

3. **Disable emoji as workaround:**
   ```json
   {
     "display": {
       "use_emoji": false
     }
   }
   ```

### Colors not showing

**Symptom:** Status line appears but without colors.

**Solutions:**

1. **Verify terminal supports 256 colors:**
   ```bash
   # macOS/Linux
   echo $TERM
   # Should be xterm-256color or similar

   # Test colors
   for i in {0..255}; do printf "\e[38;5;${i}m${i} "; done; echo
   ```

2. **Windows:** Use Windows Terminal with a color scheme enabled.

### Git segment not showing

**Symptom:** No git branch/status in status line.

**Solutions:**

1. **Verify you're in a git repository:**
   ```bash
   git status
   ```

2. **Check git is installed:**
   ```bash
   git --version
   ```

3. **Increase git timeout (if git is slow):**
   ```json
   {
     "advanced": {
       "git_timeout": 5
     }
   }
   ```

### Script errors

**Symptom:** Status line shows "ECW: Error" or similar.

**Solutions:**

1. **Enable debug mode:**
   ```bash
   # macOS
   export ECW_DEBUG=1
   echo '{"model":{"display_name":"Test"}}' | python3 ~/.claude/statusline.py
   ```

   Check stderr for error messages.

2. **Verify Python version:**
   ```bash
   python3 --version
   # Must be 3.9 or higher
   ```

3. **Check for syntax errors in config:**
   ```bash
   python3 -m json.tool ~/.claude/ecw-statusline-config.json
   ```

### Tools segment not showing data

**Symptom:** Tools segment enabled but shows nothing.

**Solutions:**

1. Tools only appear after you've used Claude Code tools (Read, Edit, Bash, etc.)

2. Verify `min_tokens` threshold isn't too high:
   ```json
   {
     "tools": {
       "enabled": true,
       "min_tokens": 10
     }
   }
   ```

3. Transcript file must exist (created automatically by Claude Code).

---

## Uninstallation

### macOS

```bash
# Remove the script
rm ~/.claude/statusline.py

# Remove configuration (optional)
rm ~/.claude/ecw-statusline-config.json

# Edit settings.json to remove statusLine section
open -e ~/.claude/settings.json
# Remove the "statusLine": { ... } section

# Restart Claude Code
```

### Linux

```bash
# Remove the script
rm ~/.claude/statusline.py

# Remove configuration (optional)
rm ~/.claude/ecw-statusline-config.json

# Edit settings.json to remove statusLine section
nano ~/.claude/settings.json
# Remove the "statusLine": { ... } section

# Restart Claude Code
```

### Windows

```powershell
# Remove the script
Remove-Item "$env:USERPROFILE\.claude\statusline.py"

# Remove configuration (optional)
Remove-Item "$env:USERPROFILE\.claude\ecw-statusline-config.json"

# Edit settings.json to remove statusLine section
notepad "$env:USERPROFILE\.claude\settings.json"
# Remove the "statusLine": { ... } section

# Restart Claude Code
```

---

## Next Steps

- Read the full [README.md](README.md) for complete configuration reference
- Enable the [Tools Segment](#enabling-the-tools-segment) to see which tools consume tokens
- Customize [thresholds](#customization-examples) based on your usage patterns
- Report issues at [GitHub Issues](https://github.com/geekatron/ecw-statusline/issues)

---

## Quick Reference Card

### File Locations

| Platform | Script | Config | Settings |
|----------|--------|--------|----------|
| macOS | `~/.claude/statusline.py` | `~/.claude/ecw-statusline-config.json` | `~/.claude/settings.json` |
| Linux | `~/.claude/statusline.py` | `~/.claude/ecw-statusline-config.json` | `~/.claude/settings.json` |
| Windows | `%USERPROFILE%\.claude\statusline.py` | `%USERPROFILE%\.claude\ecw-statusline-config.json` | `%USERPROFILE%\.claude\settings.json` |

### Status Line Segments

```
🔵/🟣/🟢 Model | 📊 Context | 💰 Cost | ⚡ Tokens | ⏱️ Session | 📉 Compaction | 🔧 Tools | 🌿 Git | 📂 Dir
```

### Color Meanings

| Color | Context | Cost |
|-------|---------|------|
| 🟢 Green | <65% | <$1 |
| 🟡 Yellow | 65-85% | $1-5 |
| 🔴 Red | >85% | >$5 |

> **Note:** Only Context and Cost segments use threshold-based coloring. Token breakdown (⚡) and Session (⏱️) use fixed informational colors.

### Debug Command

```bash
export ECW_DEBUG=1
echo '{"model":{"display_name":"Test"}}' | python3 ~/.claude/statusline.py
```
