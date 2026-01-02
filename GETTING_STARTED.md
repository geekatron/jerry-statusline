# Getting Started with ECW Status Line

A step-by-step guide to installing and configuring ECW Status Line for Claude Code.

**Primary Platform:** macOS with zsh
**Also Supported:** Windows 10/11 with PowerShell

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Verification](#verification)
4. [Configuration](#configuration)
5. [Enabling the Tools Segment](#enabling-the-tools-segment)
6. [Customization Examples](#customization-examples)
7. [Troubleshooting](#troubleshooting)
8. [Uninstallation](#uninstallation)

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

#### 4. Git (Optional)

```powershell
git --version
```

If not installed, download from [git-scm.com](https://git-scm.com/download/win).

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
🟣 Test | 📊 ~[░░░░░░░░░░] 0% | 💰 $0.00 | ⚡ 0% | ⏱️ 0m [░░░░░░░░░░] 0% | 📂 ~
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
🟣 Test | 📊 ~[░░░░░░░░░░] 0% | 💰 $0.00 | ⚡ 0% | ⏱️ 0m [░░░░░░░░░░] 0% | 📂 ~
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

## Verification

After installation, start Claude Code and verify the status line appears at the bottom of your terminal.

### What you should see

```
🟣 Sonnet | 📊 [░░░░░░░░░░] 0% | 💰 $0.00 | ⚡ 0% | ⏱️ 0m [░░░░░░░░░░] 0% | 🌿 main ✓ | ~/your-project
```

### Segment breakdown

| Segment | What it shows | Your value |
|---------|---------------|------------|
| 🟣 Sonnet | Active model | Should match your current model |
| 📊 [░░░░░░░░░░] 0% | Context window usage | Starts at 0%, increases as you chat |
| 💰 $0.00 | Session cost | Starts at $0.00, increases with usage |
| ⚡ 0% | Cache efficiency | Shows % of tokens served from cache |
| ⏱️ 0m | Session duration | Time since session started |
| 🌿 main ✓ | Git branch + status | Your current branch, ✓=clean ●=dirty |
| ~/your-project | Working directory | Your current directory |

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
| `tools.enabled` | false | Show tools segment |

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
    "cache": false,
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
| Windows | `%USERPROFILE%\.claude\statusline.py` | `%USERPROFILE%\.claude\ecw-statusline-config.json` | `%USERPROFILE%\.claude\settings.json` |

### Status Line Segments

```
🔵/🟣/🟢 Model | 📊 Context | 💰 Cost | ⚡ Cache | ⏱️ Session | 🔧 Tools | 🌿 Git | 📂 Dir
```

### Color Meanings

| Color | Context | Cost | Cache | Session |
|-------|---------|------|-------|---------|
| 🟢 Green | <65% | <$1 | >60% | <50% |
| 🟡 Yellow | 65-85% | $1-5 | 30-60% | 50-80% |
| 🔴 Red | >85% | >$5 | <30% | >80% |

### Debug Command

```bash
export ECW_DEBUG=1
echo '{"model":{"display_name":"Test"}}' | python3 ~/.claude/statusline.py
```
