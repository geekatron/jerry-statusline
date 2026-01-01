# ECW Status Line

**Evolved Claude Workflow** - A single-file, self-contained status line for Claude Code providing maximum visibility into session state, resource consumption, and workspace context.

## Overview

```
🟣 Sonnet | 📊 [▓▓▓▓░░░░░░] 42% | 💰 $1.23 | ⚡ 78% | ⏱️ 2h12m [▓▓▓▓░░░░░░] 44% | 🔧 Read:2.1k Edit:1.5k | 🌿 main ✓ | ~/project
```

### Segments

| Segment | Description | Color Logic |
|---------|-------------|-------------|
| **Model** | Active Claude model | Blue=Opus, Purple=Sonnet, Green=Haiku |
| **Context** | Context window usage | Green <65%, Yellow 65-85%, Red >85% |
| **Cost** | Session cost (USD) | Green <$1, Yellow $1-5, Red >$5 |
| **Cache** | Cache efficiency | Green >60%, Yellow 30-60%, Red <30% |
| **Session** | 5-hour block progress | Green <50%, Yellow 50-80%, Red >80% |
| **Tools** | Dominant tools by tokens | Purple (optional, requires config) |
| **Git** | Branch + status | Green=clean, Yellow=dirty |
| **Directory** | Working directory | Gray |

## Requirements

- Python 3.9+
- Claude Code CLI
- Git (optional)

## Installation

### Single-File Deployment

```bash
# 1. Download the script
curl -o ~/.claude/statusline.py https://raw.githubusercontent.com/your-org/ecw-statusline/main/statusline.py

# 2. Make executable
chmod +x ~/.claude/statusline.py

# 3. Add to ~/.claude/settings.json
```

Add to your `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/statusline.py",
    "padding": 0
  }
}
```

That's it. No additional files required.

## Configuration

ECW Status Line works out-of-the-box with sensible defaults. To customize, create an optional config file at `~/.claude/ecw-statusline-config.json`:

```json
{
  "context": {
    "warning_threshold": 0.65,
    "critical_threshold": 0.85
  },
  "cost": {
    "green_max": 1.00,
    "yellow_max": 5.00
  },
  "tools": {
    "enabled": true,
    "top_n": 3
  },
  "display": {
    "compact_mode": false
  }
}
```

Only specify values you want to override. All other settings use defaults.

### All Configuration Options

```json
{
  "display": {
    "compact_mode": false,
    "auto_compact_width": 80,
    "separator": " | ",
    "use_emoji": true,
    "progress_bar": {
      "width": 10,
      "filled_char": "▓",
      "empty_char": "░",
      "show_percentage": true
    }
  },
  "segments": {
    "model": true,
    "context": true,
    "cost": true,
    "cache": true,
    "session": true,
    "tools": true,
    "git": true,
    "directory": true
  },
  "context": {
    "warning_threshold": 0.65,
    "critical_threshold": 0.85
  },
  "cost": {
    "green_max": 1.00,
    "yellow_max": 5.00
  },
  "cache": {
    "good_threshold": 0.60,
    "warning_threshold": 0.30
  },
  "session": {
    "block_duration_seconds": 18000,
    "green_threshold": 0.50,
    "yellow_threshold": 0.80
  },
  "tools": {
    "enabled": false,
    "top_n": 3,
    "min_tokens": 100,
    "cache_ttl_seconds": 5
  },
  "git": {
    "show_branch": true,
    "show_status": true,
    "show_uncommitted_count": true,
    "max_branch_length": 20
  },
  "directory": {
    "abbreviate_home": true,
    "max_length": 25,
    "basename_only": false
  },
  "colors": {
    "green": 82,
    "yellow": 220,
    "red": 196,
    "opus": 75,
    "sonnet": 141,
    "haiku": 84,
    "separator": 240,
    "directory": 250,
    "git_clean": 82,
    "git_dirty": 220,
    "tools": 147
  },
  "advanced": {
    "handle_cumulative_bug": true,
    "git_timeout": 2,
    "debug": false
  }
}
```

## Tools Segment

The tools segment parses the Claude Code transcript JSONL file to show which tools are consuming the most tokens:

```
🔧 Read:2.1k Edit:1.5k Bash:500
```

**To enable:**

```json
{
  "tools": {
    "enabled": true,
    "top_n": 3,
    "min_tokens": 100,
    "cache_ttl_seconds": 5
  }
}
```

- `enabled`: Must be `true` to activate (default: `false`)
- `top_n`: Number of top tools to display
- `min_tokens`: Minimum tokens for a tool to appear
- `cache_ttl_seconds`: How long to cache transcript parsing results

## Compact Mode

For smaller terminals, compact mode shows only essential segments:

```
🟣 Sonnet | 📊 [▓▓▓▓░░░░░░] 42% | 💰 $1.23 | 🌿 main ✓
```

Enable via config or auto-trigger based on terminal width:

```json
{
  "display": {
    "compact_mode": true
  }
}
```

Or auto-compact when terminal is narrow:

```json
{
  "display": {
    "auto_compact_width": 80
  }
}
```

## Known Limitations

| Feature | Status | Reason |
|---------|--------|--------|
| Subscription type | Not available | Not in JSON payload |
| Per-tool breakdown | Available | Via transcript parsing |
| Accurate context after auto-compact | Partial | Known bug ([#13783](https://github.com/anthropics/claude-code/issues/13783)) |

### Context Window Bug

Claude Code has a known bug where cumulative tokens exceed context window after auto-compact. ECW Status Line handles this by:
1. Using `current_usage` fields when available
2. Displaying `~` prefix for estimated values
3. Allowing percentage to exceed 100%

## Troubleshooting

### Debug Mode

```bash
export ECW_DEBUG=1
```

Or in config:

```json
{
  "advanced": {
    "debug": true
  }
}
```

### Test Manually

```bash
echo '{"model":{"display_name":"Test"}}' | python3 ~/.claude/statusline.py
```

## Testing

```bash
python3 test_statusline.py
```

Expected: `RESULTS: 8 passed, 0 failed`

## Version History

- **2.0.0** - Single-file refactor
  - Self-contained Python script (no external files required)
  - Added Tools segment with transcript parsing
  - Added caching for transcript parsing
  - Removed external config files (embedded defaults)
  - JSON-only configuration

- **1.0.0** - Initial release

## License

MIT

## References

- [Claude Code Status Line Documentation](https://code.claude.com/docs/en/statusline)
- [GitHub Issue #13783 - Context window bug](https://github.com/anthropics/claude-code/issues/13783)
