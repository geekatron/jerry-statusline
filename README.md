# ECW Status Line

**Evolved Claude Workflow** - A high-fidelity status line for Claude Code providing maximum visibility into session state, resource consumption, and workspace context.

## Overview

ECW Status Line displays real-time information about your Claude Code session:

```
🟣 Sonnet | 📊 [▓▓▓▓░░░░░░] 42% | 💰 $1.23 | ⚡ 78% | ⏱️ 2h12m [▓▓▓▓░░░░░░] 44% | 🌿 main ✓ | ~/project
```

### Segments (Left to Right)

| Segment | Description | Color Logic |
|---------|-------------|-------------|
| **Model** | Active Claude model (Opus/Sonnet/Haiku) | Blue=Opus, Purple=Sonnet, Green=Haiku |
| **Context** | Context window usage with progress bar | Green <65%, Yellow 65-85%, Red >85% |
| **Cost** | Session cost (API-equivalent USD) | Green <$1, Yellow $1-5, Red >$5 |
| **Cache** | Cache efficiency (higher = cheaper) | Green >60%, Yellow 30-60%, Red <30% |
| **Session** | Time in 5-hour block with progress bar | Green <50%, Yellow 50-80%, Red >80% |
| **Git** | Branch name + dirty/clean status | Green=clean, Yellow=dirty with count |
| **Directory** | Current working directory | Gray (informational) |

## Requirements

- Python 3.9 or later
- Claude Code CLI
- Git (optional, for git integration)
- Terminal with 256-color and emoji support

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/ecw-statusline.git ~/.claude/ecw-statusline
```

Or copy files to your preferred location.

### 2. Verify Script Permissions

```bash
chmod +x ~/.claude/ecw-statusline/statusline.py
```

### 3. Configure Claude Code

Add the following to your `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/ecw-statusline/statusline.py",
    "padding": 0
  }
}
```

**Note**: Replace the path with your actual installation location.

### 4. Verify Installation

Run the test suite:

```bash
python3 ~/.claude/ecw-statusline/test_statusline.py
```

All 6 tests should pass.

## Configuration

ECW Status Line is fully configurable via `config.json`. All thresholds, colors, and display options can be customized.

### Configuration File Location

The configuration file must be in the same directory as `statusline.py`:

```
~/.claude/ecw-statusline/
├── statusline.py      # Main script
├── config.json        # Configuration (edit this)
├── config.yaml        # YAML reference (documentation only)
└── test_statusline.py # Test suite
```

### Key Configuration Options

#### Display Mode

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
  }
}
```

- `compact_mode`: Enable reduced segment display for small terminals
- `auto_compact_width`: Terminal width threshold for automatic compact mode (0 to disable)
- `use_emoji`: Toggle emoji icons on/off

#### Segment Visibility

```json
{
  "segments": {
    "model": true,
    "context": true,
    "cost": true,
    "cache": true,
    "session": true,
    "git": true,
    "directory": true
  }
}
```

Set any segment to `false` to hide it.

#### Thresholds

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
  "cache": {
    "good_threshold": 0.60,
    "warning_threshold": 0.30
  },
  "session": {
    "block_duration_seconds": 18000,
    "green_threshold": 0.50,
    "yellow_threshold": 0.80
  }
}
```

#### Colors (ANSI 256)

```json
{
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
    "git_dirty": 220
  }
}
```

Reference: [ANSI 256 Color Chart](https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit)

## Compact Mode

When enabled (or auto-triggered by terminal width), compact mode shows only essential segments:

```
🟣 Sonnet | 📊 [▓▓▓▓░░░░░░] 42% | 💰 $1.23 | 🌿 main ✓
```

Segments hidden in compact mode: Cache, Session, Directory

## Known Limitations

Based on verified documentation from Claude Code:

| Feature | Status | Reason |
|---------|--------|--------|
| Subscription type display | Not available | JSON payload doesn't include plan info |
| Per-tool token breakdown | Not available | JSON provides only aggregate totals |
| Operation-level tokens | Not available | Not implemented by Anthropic |
| Accurate context after auto-compact | Partial | Known bug (GitHub Issue #13783) |

### Context Window Bug Handling

Claude Code has a [known bug](https://github.com/anthropics/claude-code/issues/13783) where cumulative token counts exceed the context window after auto-compact runs. ECW Status Line handles this by:

1. Using `current_usage` fields when available (more accurate)
2. Displaying a `~` prefix when values are estimated
3. Allowing percentage to exceed 100% to make the issue visible

## Troubleshooting

### Status Line Not Appearing

1. Verify the path in `~/.claude/settings.json` is correct
2. Ensure `statusline.py` is executable: `chmod +x statusline.py`
3. Test manually: `echo '{"model":{"display_name":"Test"}}' | python3 statusline.py`

### Debug Mode

Enable debug logging by setting the environment variable:

```bash
export ECW_DEBUG=1
```

Or set in `config.json`:

```json
{
  "advanced": {
    "debug": true
  }
}
```

Debug output goes to stderr and won't affect the status line display.

### Git Information Not Showing

1. Ensure you're in a git repository
2. Check git is installed: `which git`
3. Increase timeout if git is slow: `"git_timeout": 5` in config

## Testing

Run the test suite to verify your installation:

```bash
cd ~/.claude/ecw-statusline
python3 test_statusline.py
```

Expected output: `RESULTS: 6 passed, 0 failed`

### Test Cases

| Test | Description |
|------|-------------|
| Normal Session | All metrics in green zone |
| Warning State | Context and cost in yellow zone |
| Critical State | All metrics in red zone |
| Bug Simulation | Cumulative tokens exceed window |
| Haiku Model | Verifies model tier detection |
| Minimal Payload | Edge case with missing fields |

## Architecture

```
statusline.py
├── Configuration Loading (load_config, deep_merge)
├── Data Extraction
│   ├── extract_model_info()
│   ├── extract_context_info()
│   ├── extract_cost_info()
│   ├── extract_cache_info()
│   ├── extract_session_block_info()
│   └── extract_workspace_info()
├── Git Integration (get_git_info)
├── Formatting (format_progress_bar, format_duration)
├── Segment Builders
│   ├── build_model_segment()
│   ├── build_context_segment()
│   ├── build_cost_segment()
│   ├── build_cache_segment()
│   ├── build_session_segment()
│   ├── build_git_segment()
│   └── build_directory_segment()
└── Main Builder (build_status_line)
```

## Version History

- **1.0.0** - Initial release
  - Full segment display with configurable thresholds
  - Color-coded warnings for context, cost, cache, session
  - Git integration with branch and status
  - Compact mode support
  - Known bug handling for cumulative tokens
  - Python 3.9+ compatibility (stdlib only)

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests: `python3 test_statusline.py`
4. Submit a pull request

## References

- [Claude Code Status Line Documentation](https://code.claude.com/docs/en/statusline)
- [GitHub Issue #5404 - Statusline feature documentation](https://github.com/anthropics/claude-code/issues/5404)
- [GitHub Issue #13783 - Context window cumulative bug](https://github.com/anthropics/claude-code/issues/13783)
- [MAX Plan Pricing](https://claude.com/pricing/max)
