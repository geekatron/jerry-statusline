#!/usr/bin/env python3
"""
ECW Status Line - Evolved Claude Workflow
Status line for Claude Code with maximum visibility.

Version: 1.0.0
Python: 3.9+
License: MIT

Usage:
    Receives JSON from Claude Code via stdin, outputs formatted status line.
    Configure in ~/.claude/settings.json:
    {
        "statusLine": {
            "type": "command",
            "command": "python3 /path/to/statusline.py",
            "padding": 0
        }
    }
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# =============================================================================
# CONSTANTS
# =============================================================================

VERSION = "1.0.0"
SCRIPT_DIR = Path(__file__).parent.resolve()
CONFIG_PATH = SCRIPT_DIR / "config.json"

# Default configuration (fallback if config.json not found)
DEFAULT_CONFIG: Dict[str, Any] = {
    "display": {
        "compact_mode": False,
        "auto_compact_width": 80,
        "separator": " | ",
        "use_emoji": True,
        "progress_bar": {
            "width": 10,
            "filled_char": "▓",
            "empty_char": "░",
            "show_percentage": True,
        },
    },
    "segments": {
        "model": True,
        "context": True,
        "cost": True,
        "cache": True,
        "session": True,
        "git": True,
        "directory": True,
    },
    "context": {"warning_threshold": 0.65, "critical_threshold": 0.85},
    "cost": {"green_max": 1.00, "yellow_max": 5.00},
    "cache": {"good_threshold": 0.60, "warning_threshold": 0.30},
    "session": {
        "block_duration_seconds": 18000,
        "green_threshold": 0.50,
        "yellow_threshold": 0.80,
    },
    "git": {
        "show_branch": True,
        "show_status": True,
        "show_uncommitted_count": True,
        "max_branch_length": 20,
    },
    "directory": {"abbreviate_home": True, "max_length": 25, "basename_only": False},
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
    },
    "advanced": {"handle_cumulative_bug": True, "git_timeout": 2, "debug": False},
}


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def load_config() -> Dict[str, Any]:
    """Load configuration from config.json, falling back to defaults."""
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                user_config = json.load(f)
            # Deep merge with defaults
            return deep_merge(DEFAULT_CONFIG, user_config)
        except (json.JSONDecodeError, IOError) as e:
            debug_log(f"Config load error: {e}")
    return DEFAULT_CONFIG.copy()


def deep_merge(base: Dict, override: Dict) -> Dict:
    """Recursively merge override into base dict."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def debug_log(message: str) -> None:
    """Log debug message to stderr if debug mode enabled."""
    # Note: Config not loaded yet during early calls, so check env var
    if os.environ.get("ECW_DEBUG") == "1":
        print(f"[ECW-DEBUG] {message}", file=sys.stderr)


def ansi_color(code: int) -> str:
    """Generate ANSI 256-color escape sequence."""
    if code == 0:
        return "\033[0m"  # Reset
    return f"\033[38;5;{code}m"


def ansi_reset() -> str:
    """Generate ANSI reset escape sequence."""
    return "\033[0m"


def get_terminal_width() -> int:
    """Get current terminal width."""
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 120  # Default fallback


# =============================================================================
# DATA EXTRACTION
# =============================================================================


def safe_get(data: Dict, *keys, default: Any = None) -> Any:
    """Safely navigate nested dict keys."""
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current if current is not None else default


def extract_model_info(data: Dict) -> Tuple[str, str]:
    """Extract model display name and tier."""
    display_name = safe_get(data, "model", "display_name", default="Unknown")
    model_id = safe_get(data, "model", "id", default="").lower()

    # Determine tier from model ID
    if "opus" in model_id:
        tier = "opus"
    elif "haiku" in model_id:
        tier = "haiku"
    else:
        tier = "sonnet"  # Default to sonnet for unknown

    return display_name, tier


def extract_context_info(data: Dict, config: Dict) -> Tuple[float, int, int, bool]:
    """
    Extract context window usage.
    Returns: (percentage, used_tokens, total_tokens, is_estimated)

    Handles the known bug where cumulative tokens exceed context window
    by using current_usage when available.
    """
    context_window_size = safe_get(
        data, "context_window", "context_window_size", default=200000
    )

    # Try to use current_usage (more accurate for actual context)
    current_usage = safe_get(data, "context_window", "current_usage")

    if current_usage:
        input_tokens = safe_get(current_usage, "input_tokens", default=0)
        cache_creation = safe_get(
            current_usage, "cache_creation_input_tokens", default=0
        )
        cache_read = safe_get(current_usage, "cache_read_input_tokens", default=0)
        used_tokens = input_tokens + cache_creation + cache_read
        is_estimated = False
    else:
        # Fall back to cumulative totals (may be inaccurate after auto-compact)
        used_tokens = safe_get(
            data, "context_window", "total_input_tokens", default=0
        )
        is_estimated = True

    # Handle the cumulative bug: cap at 100% but mark as estimated
    if used_tokens > context_window_size:
        if config["advanced"]["handle_cumulative_bug"]:
            is_estimated = True
            # Don't cap the display, but mark it

    percentage = (used_tokens / context_window_size) if context_window_size > 0 else 0

    return percentage, used_tokens, context_window_size, is_estimated


def extract_cost_info(data: Dict) -> Tuple[float, int, int]:
    """Extract cost and duration info."""
    cost_usd = safe_get(data, "cost", "total_cost_usd", default=0.0)
    duration_ms = safe_get(data, "cost", "total_duration_ms", default=0)
    lines_added = safe_get(data, "cost", "total_lines_added", default=0)
    lines_removed = safe_get(data, "cost", "total_lines_removed", default=0)

    return cost_usd, duration_ms, lines_added - lines_removed


def extract_cache_info(data: Dict) -> float:
    """
    Calculate cache efficiency as ratio of cache reads to total input.
    Higher = better (more tokens served from cache = cheaper).
    """
    current_usage = safe_get(data, "context_window", "current_usage")

    if not current_usage:
        return 0.0

    input_tokens = safe_get(current_usage, "input_tokens", default=0)
    cache_read = safe_get(current_usage, "cache_read_input_tokens", default=0)

    total_input = input_tokens + cache_read
    if total_input == 0:
        return 0.0

    return cache_read / total_input


def extract_session_block_info(data: Dict, config: Dict) -> Tuple[float, int]:
    """
    Calculate progress through 5-hour session block.
    Returns: (percentage, elapsed_seconds)
    """
    duration_ms = safe_get(data, "cost", "total_duration_ms", default=0)
    elapsed_seconds = duration_ms // 1000

    block_duration = config["session"]["block_duration_seconds"]
    percentage = elapsed_seconds / block_duration if block_duration > 0 else 0

    return min(percentage, 1.0), elapsed_seconds


def extract_workspace_info(data: Dict, config: Dict) -> str:
    """Extract and format workspace directory."""
    current_dir = safe_get(data, "workspace", "current_dir", default="")

    if not current_dir:
        current_dir = safe_get(data, "cwd", default="~")

    dir_config = config["directory"]

    # Abbreviate home directory
    if dir_config["abbreviate_home"]:
        home = os.path.expanduser("~")
        if current_dir.startswith(home):
            current_dir = "~" + current_dir[len(home):]

    # Use basename only
    if dir_config["basename_only"]:
        current_dir = os.path.basename(current_dir) or current_dir

    # Truncate if too long
    max_len = dir_config["max_length"]
    if len(current_dir) > max_len:
        current_dir = "..." + current_dir[-(max_len - 3):]

    return current_dir


# =============================================================================
# GIT INTEGRATION
# =============================================================================


def get_git_info(data: Dict, config: Dict) -> Optional[Tuple[str, bool, int]]:
    """
    Get git branch, status, and uncommitted file count.
    Returns: (branch_name, is_clean, uncommitted_count) or None if not a git repo.
    """
    git_config = config["git"]
    timeout = config["advanced"]["git_timeout"]

    # Get working directory
    cwd = safe_get(data, "workspace", "current_dir") or safe_get(data, "cwd")
    if not cwd:
        return None

    try:
        # Check if in git repo and get branch name
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode != 0:
            return None

        branch = result.stdout.strip()

        # Truncate branch name if needed
        max_len = git_config["max_branch_length"]
        if len(branch) > max_len:
            branch = branch[: max_len - 3] + "..."

        # Get status (uncommitted files)
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        uncommitted_lines = [
            line for line in result.stdout.strip().split("\n") if line
        ]
        uncommitted_count = len(uncommitted_lines)
        is_clean = uncommitted_count == 0

        return branch, is_clean, uncommitted_count

    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
        debug_log(f"Git error: {e}")
        return None


# =============================================================================
# FORMATTING FUNCTIONS
# =============================================================================


def format_progress_bar(
    percentage: float, config: Dict, color_code: int
) -> str:
    """Format a progress bar with color."""
    bar_config = config["display"]["progress_bar"]
    width = bar_config["width"]
    filled_char = bar_config["filled_char"]
    empty_char = bar_config["empty_char"]
    show_pct = bar_config["show_percentage"]

    # Clamp percentage to 0-1 for display (but allow showing >100% in number)
    display_pct = min(max(percentage, 0), 1.0)
    filled_count = int(display_pct * width)
    empty_count = width - filled_count

    bar = filled_char * filled_count + empty_char * empty_count
    color = ansi_color(color_code)
    reset = ansi_reset()

    if show_pct:
        pct_str = f"{int(percentage * 100)}%"
        return f"{color}[{bar}] {pct_str}{reset}"
    else:
        return f"{color}[{bar}]{reset}"


def format_duration(seconds: int) -> str:
    """Format duration as HhMm or Mm."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours > 0:
        return f"{hours}h{minutes:02d}m"
    else:
        return f"{minutes}m"


def get_threshold_color(
    value: float,
    green_max: float,
    yellow_max: float,
    colors: Dict,
    invert: bool = False,
) -> int:
    """
    Get color code based on threshold.
    If invert=True, lower values are worse (used for cache efficiency).
    """
    if invert:
        # Higher is better (cache efficiency)
        if value >= green_max:
            return colors["green"]
        elif value >= yellow_max:
            return colors["yellow"]
        else:
            return colors["red"]
    else:
        # Lower is better (context usage, cost)
        if value <= green_max:
            return colors["green"]
        elif value <= yellow_max:
            return colors["yellow"]
        else:
            return colors["red"]


# =============================================================================
# SEGMENT BUILDERS
# =============================================================================


def build_model_segment(data: Dict, config: Dict) -> str:
    """Build the model display segment."""
    display_name, tier = extract_model_info(data)
    colors = config["colors"]

    # Model tier icons
    icons = {"opus": "🔵", "sonnet": "🟣", "haiku": "🟢"}
    icon = icons.get(tier, "⚪") if config["display"]["use_emoji"] else ""

    color = ansi_color(colors.get(tier, colors["sonnet"]))
    reset = ansi_reset()

    if icon:
        return f"{color}{icon} {display_name}{reset}"
    else:
        return f"{color}{display_name}{reset}"


def build_context_segment(data: Dict, config: Dict) -> str:
    """Build the context window usage segment."""
    percentage, used, total, is_estimated = extract_context_info(data, config)
    colors = config["colors"]
    thresholds = config["context"]

    color_code = get_threshold_color(
        percentage,
        thresholds["warning_threshold"],
        thresholds["critical_threshold"],
        colors,
    )

    icon = "📊 " if config["display"]["use_emoji"] else ""
    estimate_marker = "~" if is_estimated else ""

    bar = format_progress_bar(percentage, config, color_code)

    return f"{icon}{estimate_marker}{bar}"


def build_cost_segment(data: Dict, config: Dict) -> str:
    """Build the cost display segment."""
    cost_usd, _, _ = extract_cost_info(data)
    colors = config["colors"]
    thresholds = config["cost"]

    color_code = get_threshold_color(
        cost_usd, thresholds["green_max"], thresholds["yellow_max"], colors
    )

    icon = "💰 " if config["display"]["use_emoji"] else "$"
    color = ansi_color(color_code)
    reset = ansi_reset()

    return f"{icon}{color}${cost_usd:.2f}{reset}"


def build_cache_segment(data: Dict, config: Dict) -> str:
    """Build the cache efficiency segment."""
    cache_ratio = extract_cache_info(data)
    colors = config["colors"]
    thresholds = config["cache"]

    color_code = get_threshold_color(
        cache_ratio,
        thresholds["good_threshold"],
        thresholds["warning_threshold"],
        colors,
        invert=True,  # Higher is better for cache
    )

    icon = "⚡ " if config["display"]["use_emoji"] else ""
    color = ansi_color(color_code)
    reset = ansi_reset()

    pct = int(cache_ratio * 100)
    return f"{icon}{color}{pct}%{reset}"


def build_session_segment(data: Dict, config: Dict) -> str:
    """Build the session block timer segment."""
    percentage, elapsed_seconds = extract_session_block_info(data, config)
    colors = config["colors"]
    thresholds = config["session"]

    color_code = get_threshold_color(
        percentage, thresholds["green_threshold"], thresholds["yellow_threshold"], colors
    )

    icon = "⏱️ " if config["display"]["use_emoji"] else ""
    duration_str = format_duration(elapsed_seconds)

    bar = format_progress_bar(percentage, config, color_code)

    return f"{icon}{duration_str} {bar}"


def build_git_segment(data: Dict, config: Dict) -> str:
    """Build the git status segment."""
    git_info = get_git_info(data, config)

    if git_info is None:
        return ""

    branch, is_clean, uncommitted_count = git_info
    colors = config["colors"]
    git_config = config["git"]

    icon = "🌿 " if config["display"]["use_emoji"] else ""

    if is_clean:
        status_icon = "✓" if git_config["show_status"] else ""
        color = ansi_color(colors["git_clean"])
    else:
        if git_config["show_uncommitted_count"]:
            status_icon = f"●{uncommitted_count}"
        elif git_config["show_status"]:
            status_icon = "●"
        else:
            status_icon = ""
        color = ansi_color(colors["git_dirty"])

    reset = ansi_reset()

    return f"{icon}{color}{branch} {status_icon}{reset}".strip()


def build_directory_segment(data: Dict, config: Dict) -> str:
    """Build the directory display segment."""
    directory = extract_workspace_info(data, config)
    colors = config["colors"]

    icon = "📂 " if config["display"]["use_emoji"] else ""
    color = ansi_color(colors["directory"])
    reset = ansi_reset()

    return f"{icon}{color}{directory}{reset}"


# =============================================================================
# MAIN BUILDER
# =============================================================================


def build_status_line(data: Dict, config: Dict) -> str:
    """Build the complete status line from all segments."""
    segments_config = config["segments"]
    display_config = config["display"]
    separator = display_config["separator"]
    colors = config["colors"]

    # Determine if compact mode should be used
    compact = display_config["compact_mode"]
    if not compact and display_config["auto_compact_width"] > 0:
        term_width = get_terminal_width()
        if term_width < display_config["auto_compact_width"]:
            compact = True

    # Build enabled segments
    segments = []

    if segments_config["model"]:
        segments.append(build_model_segment(data, config))

    if segments_config["context"]:
        segments.append(build_context_segment(data, config))

    if segments_config["cost"]:
        segments.append(build_cost_segment(data, config))

    # Skip these in compact mode
    if not compact:
        if segments_config["cache"]:
            segments.append(build_cache_segment(data, config))

        if segments_config["session"]:
            segments.append(build_session_segment(data, config))

    if segments_config["git"]:
        git_segment = build_git_segment(data, config)
        if git_segment:  # Only add if in a git repo
            segments.append(git_segment)

    if segments_config["directory"] and not compact:
        segments.append(build_directory_segment(data, config))

    # Join with colored separator
    sep_color = ansi_color(colors["separator"])
    reset = ansi_reset()
    colored_sep = f"{sep_color}{separator}{reset}"

    return colored_sep.join(segments)


# =============================================================================
# ENTRY POINT
# =============================================================================


def main() -> None:
    """Main entry point."""
    try:
        # Load configuration
        config = load_config()

        if config["advanced"]["debug"]:
            os.environ["ECW_DEBUG"] = "1"

        # Read JSON from stdin
        input_data = sys.stdin.read().strip()

        if not input_data:
            debug_log("No input received")
            print("ECW: No data")
            return

        try:
            data = json.loads(input_data)
        except json.JSONDecodeError as e:
            debug_log(f"JSON parse error: {e}")
            print("ECW: Parse error")
            return

        # Build and output status line
        status_line = build_status_line(data, config)
        print(status_line)

    except Exception as e:
        debug_log(f"Unexpected error: {e}")
        print(f"ECW: Error - {type(e).__name__}")


if __name__ == "__main__":
    main()
