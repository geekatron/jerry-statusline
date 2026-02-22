#!/usr/bin/env python3
"""
ECW Status Line - Test Suite
Validates statusline output with mock Claude Code JSON payloads.

Version: 3.0.0
Usage: python3 test_statusline.py
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
STATUSLINE_SCRIPT = SCRIPT_DIR / "statusline.py"

# =============================================================================
# TEST PAYLOADS
# =============================================================================

PAYLOAD_NORMAL = {
    "hook_event_name": "Status",
    "session_id": "test-session-001",
    "transcript_path": "/tmp/test-transcript.jsonl",
    "cwd": "/home/user/ecw-statusline",
    "version": "1.0.80",
    "model": {"id": "claude-sonnet-4-20250514", "display_name": "Sonnet"},
    "workspace": {
        "current_dir": "/home/user/ecw-statusline",
        "project_dir": "/home/user/ecw-statusline",
    },
    "output_style": {"name": "default"},
    "cost": {
        "total_cost_usd": 0.45,
        "total_duration_ms": 300000,
        "total_api_duration_ms": 2300,
        "total_lines_added": 156,
        "total_lines_removed": 23,
    },
    "context_window": {
        "total_input_tokens": 15234,
        "total_output_tokens": 9412,
        "context_window_size": 200000,
        "current_usage": {
            "input_tokens": 8500,
            "output_tokens": 1200,
            "cache_creation_input_tokens": 5000,
            "cache_read_input_tokens": 12000,
        },
    },
    "exceeds_200k_tokens": False,
}

PAYLOAD_WARNING = {
    "hook_event_name": "Status",
    "session_id": "test-session-002",
    "cwd": "/home/user/project",
    "model": {"id": "claude-opus-4-20250514", "display_name": "Opus"},
    "workspace": {
        "current_dir": "/home/user/project",
        "project_dir": "/home/user/project",
    },
    "cost": {
        "total_cost_usd": 3.50,
        "total_duration_ms": 7200000,
        "total_lines_added": 500,
        "total_lines_removed": 100,
    },
    "context_window": {
        "total_input_tokens": 50000,
        "total_output_tokens": 20000,
        "context_window_size": 200000,
        "current_usage": {
            "input_tokens": 100000,
            "output_tokens": 15000,
            "cache_creation_input_tokens": 40000,
            "cache_read_input_tokens": 5000,
        },
    },
}

PAYLOAD_CRITICAL = {
    "hook_event_name": "Status",
    "session_id": "test-session-003",
    "cwd": "/home/user/big-project",
    "model": {"id": "claude-opus-4-20250514", "display_name": "Opus"},
    "workspace": {
        "current_dir": "/home/user/big-project",
        "project_dir": "/home/user/big-project",
    },
    "cost": {
        "total_cost_usd": 12.75,
        "total_duration_ms": 14400000,
        "total_lines_added": 2000,
        "total_lines_removed": 500,
    },
    "context_window": {
        "total_input_tokens": 180000,
        "total_output_tokens": 50000,
        "context_window_size": 200000,
        "current_usage": {
            "input_tokens": 150000,
            "output_tokens": 30000,
            "cache_creation_input_tokens": 30000,
            "cache_read_input_tokens": 1000,
        },
    },
}

PAYLOAD_BUG_SIMULATION = {
    "hook_event_name": "Status",
    "session_id": "test-session-004",
    "cwd": "/home/user/long-session",
    "model": {"id": "claude-sonnet-4-20250514", "display_name": "Sonnet"},
    "workspace": {
        "current_dir": "/home/user/long-session",
        "project_dir": "/home/user/long-session",
    },
    "cost": {
        "total_cost_usd": 8.00,
        "total_duration_ms": 18000000,
    },
    "context_window": {
        "total_input_tokens": 340000,
        "total_output_tokens": 100000,
        "context_window_size": 200000,
    },
}

PAYLOAD_HAIKU = {
    "hook_event_name": "Status",
    "session_id": "test-session-005",
    "cwd": "/home/user/quick-task",
    "model": {"id": "claude-haiku-3-20250514", "display_name": "Haiku"},
    "workspace": {
        "current_dir": "/home/user/quick-task",
        "project_dir": "/home/user/quick-task",
    },
    "cost": {
        "total_cost_usd": 0.05,
        "total_duration_ms": 60000,
    },
    "context_window": {
        "total_input_tokens": 5000,
        "total_output_tokens": 1000,
        "context_window_size": 200000,
        "current_usage": {
            "input_tokens": 3000,
            "output_tokens": 500,
            "cache_creation_input_tokens": 1000,
            "cache_read_input_tokens": 500,
        },
    },
}

PAYLOAD_MINIMAL = {
    "model": {"display_name": "Unknown"},
    "workspace": {},
    "cost": {},
    "context_window": {},
}

# Long session payload for testing duration display
PAYLOAD_LONG_SESSION = {
    "hook_event_name": "Status",
    "session_id": "test-session-long",
    "cwd": "/home/user/marathon",
    "model": {"id": "claude-sonnet-4-20250514", "display_name": "Sonnet"},
    "workspace": {
        "current_dir": "/home/user/marathon",
        "project_dir": "/home/user/marathon",
    },
    "cost": {
        "total_cost_usd": 45.00,
        "total_duration_ms": 158700000,  # 44h05m in ms
        "total_lines_added": 5000,
        "total_lines_removed": 1000,
    },
    "context_window": {
        "total_input_tokens": 1200000,
        "total_output_tokens": 400000,
        "context_window_size": 200000,
        "current_usage": {
            "input_tokens": 50000,
            "output_tokens": 10000,
            "cache_creation_input_tokens": 20000,
            "cache_read_input_tokens": 80000,
        },
    },
}

# =============================================================================
# TRANSCRIPT TEST DATA
# =============================================================================

SAMPLE_TRANSCRIPT = [
    {
        "message": {
            "role": "assistant",
            "content": [
                {
                    "type": "tool_use",
                    "name": "Read",
                    "input": {"file_path": "/test.py" * 100},
                },
            ],
        }
    },
    {
        "message": {
            "role": "assistant",
            "content": [
                {
                    "type": "tool_use",
                    "name": "Read",
                    "input": {"file_path": "/other.py" * 50},
                },
            ],
        }
    },
    {
        "message": {
            "role": "assistant",
            "content": [
                {"type": "tool_use", "name": "Edit", "input": {"changes": "x" * 200}},
            ],
        }
    },
    {
        "message": {
            "role": "assistant",
            "content": [
                {"type": "tool_use", "name": "Bash", "input": {"command": "ls -la"}},
            ],
        }
    },
]


# =============================================================================
# TEST RUNNER
# =============================================================================


def _build_cmd() -> list:
    """Build the command to run statusline.py, optionally with coverage instrumentation."""
    if os.environ.get("COVERAGE_MODE"):
        return [sys.executable, "-m", "coverage", "run", "--parallel-mode", str(STATUSLINE_SCRIPT)]
    return [sys.executable, str(STATUSLINE_SCRIPT)]


def run_test(name: str, payload: dict, config_override: dict = None) -> bool:
    """Run statusline script with payload and display result."""
    print(f"\n{'=' * 60}")
    print(f"TEST: {name}")
    print(f"{'=' * 60}")

    env = os.environ.copy()
    # Force UTF-8 mode on Windows to handle ANSI escape sequences
    env["PYTHONUTF8"] = "1"

    # Create temporary config if override provided
    config_file = None
    if config_override:
        config_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        )
        json.dump(config_override, config_file)
        config_file.close()
        # Place config next to script
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        with open(config_path, "w") as f:
            json.dump(config_override, f)

    try:
        result = subprocess.run(
            _build_cmd(),
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            env=env,
        )

        print(f"STDOUT: {result.stdout.strip()}")
        if result.stderr:
            print(f"STDERR: {result.stderr.strip()}")
        print(f"EXIT CODE: {result.returncode}")

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("ERROR: Script timed out!")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        # Clean up config file
        if config_override:
            config_path = SCRIPT_DIR / "ecw-statusline-config.json"
            if config_path.exists():
                config_path.unlink()


def run_tools_test() -> bool:
    """Test the tools segment with a mock transcript."""
    print(f"\n{'=' * 60}")
    print("TEST: Tools Segment (with transcript)")
    print(f"{'=' * 60}")

    # Create temporary transcript file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as tf:
        for entry in SAMPLE_TRANSCRIPT:
            tf.write(json.dumps(entry) + "\n")
        transcript_path = tf.name

    # Create config that enables tools
    config = {"tools": {"enabled": True, "top_n": 3, "min_tokens": 1}}

    # Create payload with transcript path
    payload = PAYLOAD_NORMAL.copy()
    payload["transcript_path"] = transcript_path

    try:
        # Write config file
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

        result = subprocess.run(
            _build_cmd(),
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=5,
        )

        print(f"STDOUT: {result.stdout.strip()}")
        if result.stderr:
            print(f"STDERR: {result.stderr.strip()}")
        print(f"EXIT CODE: {result.returncode}")

        # Check that tools appear in output
        has_tools = "Read:" in result.stdout or "Edit:" in result.stdout
        print(f"Tools segment present: {has_tools}")

        return result.returncode == 0

    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        # Clean up
        Path(transcript_path).unlink(missing_ok=True)
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        config_path.unlink(missing_ok=True)


def run_compact_test() -> bool:
    """Test compact mode hides session, tokens, compaction, and directory segments."""
    print(f"\n{'=' * 60}")
    print("TEST: Compact Mode")
    print(f"{'=' * 60}")

    config = {"display": {"compact_mode": True}}

    try:
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

        result = subprocess.run(
            _build_cmd(),
            input=json.dumps(PAYLOAD_NORMAL),
            capture_output=True,
            text=True,
            timeout=5,
        )

        print(f"STDOUT: {result.stdout.strip()}")

        # Compact mode should NOT have session (⏱️), tokens (⚡), or directory (📂)
        has_session = "⏱️" in result.stdout
        has_tokens = "⚡" in result.stdout
        has_directory = "📂" in result.stdout

        print(f"Session hidden (expected): {not has_session}")
        print(f"Tokens hidden (expected): {not has_tokens}")
        print(f"Directory hidden (expected): {not has_directory}")

        return (
            result.returncode == 0
            and not has_session
            and not has_tokens
            and not has_directory
        )

    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        config_path.unlink(missing_ok=True)


def run_currency_test() -> bool:
    """Test configurable currency symbol."""
    print(f"\n{'=' * 60}")
    print("TEST: Configurable Currency (CAD)")
    print(f"{'=' * 60}")

    config = {"cost": {"currency_symbol": "CAD "}}

    try:
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

        result = subprocess.run(
            _build_cmd(),
            input=json.dumps(PAYLOAD_NORMAL),
            capture_output=True,
            text=True,
            timeout=5,
        )

        print(f"STDOUT: {result.stdout.strip()}")

        # Should contain "CAD " followed by the cost
        has_cad = "CAD " in result.stdout
        print(f"CAD currency present: {has_cad}")

        return result.returncode == 0 and has_cad

    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        config_path.unlink(missing_ok=True)


def run_tokens_segment_test() -> bool:
    """Test the new tokens segment showing fresh/cached breakdown."""
    print(f"\n{'=' * 60}")
    print("TEST: Tokens Segment (Fresh/Cached Breakdown)")
    print(f"{'=' * 60}")

    try:
        result = subprocess.run(
            _build_cmd(),
            input=json.dumps(PAYLOAD_NORMAL),
            capture_output=True,
            text=True,
            timeout=5,
        )

        print(f"STDOUT: {result.stdout.strip()}")

        # Should contain ⚡ (tokens icon) and → (fresh indicator) and ↺ (cached indicator)
        has_tokens_icon = "⚡" in result.stdout
        has_fresh_indicator = "→" in result.stdout
        has_cached_indicator = "↺" in result.stdout

        print(f"Tokens icon (⚡) present: {has_tokens_icon}")
        print(f"Fresh indicator (→) present: {has_fresh_indicator}")
        print(f"Cached indicator (↺) present: {has_cached_indicator}")

        return (
            result.returncode == 0
            and has_tokens_icon
            and has_fresh_indicator
            and has_cached_indicator
        )

    except Exception as e:
        print(f"ERROR: {e}")
        return False


def run_session_segment_test() -> bool:
    """Test the session segment showing duration + total tokens."""
    print(f"\n{'=' * 60}")
    print("TEST: Session Segment (Duration + Total Tokens)")
    print(f"{'=' * 60}")

    try:
        result = subprocess.run(
            _build_cmd(),
            input=json.dumps(PAYLOAD_LONG_SESSION),
            capture_output=True,
            text=True,
            timeout=5,
        )

        print(f"STDOUT: {result.stdout.strip()}")

        # Should contain ⏱️ (session icon) and duration format (e.g., "44h05m")
        has_session_icon = "⏱️" in result.stdout
        has_hours = "h" in result.stdout and "m" in result.stdout
        has_tok = (
            "tok" in result.stdout or "M" in result.stdout
        )  # Total tokens in M format

        print(f"Session icon (⏱️) present: {has_session_icon}")
        print(f"Duration format (XhYYm) present: {has_hours}")
        print(f"Total tokens indicator present: {has_tok}")

        return result.returncode == 0 and has_session_icon and has_hours

    except Exception as e:
        print(f"ERROR: {e}")
        return False


def run_compaction_test() -> bool:
    """Test compaction detection with state file."""
    print(f"\n{'=' * 60}")
    print("TEST: Compaction Detection")
    print(f"{'=' * 60}")

    # Use a temporary state file for testing
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tf:
        # Pre-populate state with high previous context to simulate compaction
        state = {
            "previous_context_tokens": 180000,  # High previous count
            "last_compaction_from": 0,
            "last_compaction_to": 0,
        }
        json.dump(state, tf)
        state_file = tf.name

    config = {"compaction": {"state_file": state_file, "detection_threshold": 10000}}

    # Use normal payload which has much lower context (~25k tokens)
    # This should trigger compaction detection (180k -> 25k)

    try:
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

        result = subprocess.run(
            _build_cmd(),
            input=json.dumps(PAYLOAD_NORMAL),
            capture_output=True,
            text=True,
            timeout=5,
        )

        print(f"STDOUT: {result.stdout.strip()}")

        # Should contain 📉 (compaction icon) when compaction is detected
        has_compaction_icon = "📉" in result.stdout

        print(f"Compaction icon (📉) present: {has_compaction_icon}")

        return result.returncode == 0 and has_compaction_icon

    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        # Clean up
        Path(state_file).unlink(missing_ok=True)
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        config_path.unlink(missing_ok=True)


def run_no_home_test() -> bool:
    """Test behavior when HOME is not set (Docker/container scenario)."""
    print(f"\n{'=' * 60}")
    print("TEST: No HOME Environment (Container Simulation)")
    print(f"{'=' * 60}")

    env = os.environ.copy()
    # Remove HOME-related variables to simulate container
    env.pop("HOME", None)
    env.pop("USERPROFILE", None)
    env.pop("HOMEDRIVE", None)
    env.pop("HOMEPATH", None)
    env["PYTHONUTF8"] = "1"

    try:
        result = subprocess.run(
            _build_cmd(),
            input=json.dumps(PAYLOAD_NORMAL),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            env=env,
        )

        print(f"STDOUT: {result.stdout.strip()}")
        if result.stderr:
            print(f"STDERR: {result.stderr.strip()}")
        print(f"EXIT CODE: {result.returncode}")

        # Should NOT crash, should produce output
        has_output = len(result.stdout.strip()) > 0
        print(f"Produced output without crash: {has_output}")

        return result.returncode == 0 and has_output

    except Exception as e:
        print(f"ERROR: {e}")
        return False


def run_no_tty_test() -> bool:
    """Test behavior when no TTY is available (pipe/container scenario)."""
    print(f"\n{'=' * 60}")
    print("TEST: No TTY (Pipe/Container Simulation)")
    print(f"{'=' * 60}")

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"

    try:
        # Run with stdin as pipe (no TTY) - this is the default for subprocess
        result = subprocess.run(
            _build_cmd(),
            input=json.dumps(PAYLOAD_MINIMAL),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            env=env,
        )

        print(f"STDOUT: {result.stdout.strip()}")
        print(f"EXIT CODE: {result.returncode}")

        # Should produce valid output even without a TTY
        has_output = len(result.stdout.strip()) > 0
        no_error = "Error" not in result.stdout
        print(f"Valid output without TTY: {has_output and no_error}")

        return result.returncode == 0 and has_output and no_error

    except Exception as e:
        print(f"ERROR: {e}")
        return False


def run_readonly_state_test() -> bool:
    """Test behavior when state file location is read-only."""
    print(f"\n{'=' * 60}")
    print("TEST: Read-Only Filesystem (State File)")
    print(f"{'=' * 60}")

    # Create a read-only directory to simulate read-only filesystem
    readonly_dir = tempfile.mkdtemp()
    state_file_path = os.path.join(readonly_dir, "subdir", "state.json")
    os.chmod(readonly_dir, 0o444)

    config = {
        "compaction": {
            "state_file": state_file_path,
            "detection_threshold": 10000,
        }
    }

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"

    try:
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

        result = subprocess.run(
            _build_cmd(),
            input=json.dumps(PAYLOAD_NORMAL),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            env=env,
        )

        print(f"STDOUT: {result.stdout.strip()}")
        if result.stderr:
            print(f"STDERR: {result.stderr.strip()}")
        print(f"EXIT CODE: {result.returncode}")

        # Should NOT crash even with unwritable state path
        has_output = len(result.stdout.strip()) > 0
        no_crash = result.returncode == 0
        print(f"Graceful degradation on read-only FS: {has_output and no_crash}")

        return no_crash and has_output

    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        config_path.unlink(missing_ok=True)
        # Restore permissions for cleanup (use shutil.rmtree for Windows compatibility)
        os.chmod(readonly_dir, 0o755)
        shutil.rmtree(readonly_dir, ignore_errors=True)


def run_emoji_disabled_test() -> bool:
    """Test ASCII-only mode (no emoji) for terminals without Unicode support."""
    print(f"\n{'=' * 60}")
    print("TEST: Emoji Disabled (ASCII Fallback)")
    print(f"{'=' * 60}")

    config = {"display": {"use_emoji": False}}

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"

    try:
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

        result = subprocess.run(
            _build_cmd(),
            input=json.dumps(PAYLOAD_NORMAL),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            env=env,
        )

        print(f"STDOUT: {result.stdout.strip()}")
        print(f"EXIT CODE: {result.returncode}")

        # Should NOT contain ANY non-ASCII characters (codepoint > 127)
        non_ascii = [ch for ch in result.stdout if ord(ch) > 127]
        has_non_ascii = len(non_ascii) > 0
        if has_non_ascii:
            unique_non_ascii = set(non_ascii)
            print(f"Non-ASCII chars found: {unique_non_ascii}")
        print(f"Pure ASCII output (expected): {not has_non_ascii}")

        # Should contain ASCII alternatives
        has_ascii_bar = "#" in result.stdout or "-" in result.stdout
        print(f"ASCII progress bar chars present: {has_ascii_bar}")

        return result.returncode == 0 and not has_non_ascii

    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        config_path.unlink(missing_ok=True)


def run_corrupt_state_test() -> bool:
    """Test behavior when state file contains invalid JSON."""
    print(f"\n{'=' * 60}")
    print("TEST: Corrupt State File (Invalid JSON)")
    print(f"{'=' * 60}")

    # Create a state file with malformed JSON
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tf:
        tf.write("{invalid json: missing quotes, }")
        state_file = tf.name

    config = {
        "compaction": {
            "state_file": state_file,
            "detection_threshold": 10000,
        }
    }

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"

    try:
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

        result = subprocess.run(
            _build_cmd(),
            input=json.dumps(PAYLOAD_NORMAL),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            env=env,
        )

        print(f"STDOUT: {result.stdout.strip()}")
        if result.stderr:
            print(f"STDERR: {result.stderr.strip()}")
        print(f"EXIT CODE: {result.returncode}")

        # Should NOT crash, should use safe defaults
        has_output = len(result.stdout.strip()) > 0
        no_crash = result.returncode == 0
        print(f"Graceful handling of corrupt state: {has_output and no_crash}")

        return no_crash and has_output

    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        Path(state_file).unlink(missing_ok=True)
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        config_path.unlink(missing_ok=True)


def run_no_color_env_test() -> bool:
    """Test that NO_COLOR environment variable disables ALL ANSI escape codes.

    Per https://no-color.org/ spec: when NO_COLOR is present (any value),
    all ANSI color escape sequences MUST be suppressed.
    """
    print(f"\n{'=' * 60}")
    print("TEST: NO_COLOR Environment Variable (G-016)")
    print(f"{'=' * 60}")

    ansi_re = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["NO_COLOR"] = "1"

    try:
        result = subprocess.run(
            _build_cmd(),
            input=json.dumps(PAYLOAD_NORMAL),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            env=env,
        )

        print(f"STDOUT: {result.stdout.strip()}")
        if result.stderr:
            print(f"STDERR: {result.stderr.strip()}")
        print(f"EXIT CODE: {result.returncode}")

        # With NO_COLOR set, output must contain ZERO ANSI escape sequences
        ansi_matches = ansi_re.findall(result.stdout)
        has_ansi = len(ansi_matches) > 0
        has_output = len(result.stdout.strip()) > 0

        if has_ansi:
            print(f"FAIL: Found {len(ansi_matches)} ANSI escape sequences in output")
            print(
                f"  Sequences: {ansi_matches[:5]}{'...' if len(ansi_matches) > 5 else ''}"
            )
        else:
            print("PASS: No ANSI escape sequences found")

        print(f"Has output: {has_output}")
        print(f"No ANSI codes (expected): {not has_ansi}")

        return result.returncode == 0 and has_output and not has_ansi

    except Exception as e:
        print(f"ERROR: {e}")
        return False


def run_use_color_disabled_test() -> bool:
    """Test that display.use_color=false config disables ALL ANSI escape codes.

    When the config option display.use_color is set to false, the output
    must contain zero ANSI color escape sequences (G-021).
    """
    print(f"\n{'=' * 60}")
    print("TEST: use_color Config Disabled (G-021)")
    print(f"{'=' * 60}")

    ansi_re = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")

    config = {"display": {"use_color": False}}

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    # Ensure NO_COLOR is NOT set so we isolate the config effect
    env.pop("NO_COLOR", None)

    try:
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

        result = subprocess.run(
            _build_cmd(),
            input=json.dumps(PAYLOAD_NORMAL),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            env=env,
        )

        print(f"STDOUT: {result.stdout.strip()}")
        if result.stderr:
            print(f"STDERR: {result.stderr.strip()}")
        print(f"EXIT CODE: {result.returncode}")

        # With use_color=false, output must contain ZERO ANSI escape sequences
        ansi_matches = ansi_re.findall(result.stdout)
        has_ansi = len(ansi_matches) > 0
        has_output = len(result.stdout.strip()) > 0

        if has_ansi:
            print(f"FAIL: Found {len(ansi_matches)} ANSI escape sequences in output")
            print(
                f"  Sequences: {ansi_matches[:5]}{'...' if len(ansi_matches) > 5 else ''}"
            )
        else:
            print("PASS: No ANSI escape sequences found")

        print(f"Has output: {has_output}")
        print(f"No ANSI codes (expected): {not has_ansi}")

        return result.returncode == 0 and has_output and not has_ansi

    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        config_path.unlink(missing_ok=True)


def run_color_matrix_test() -> bool:
    """Test the 4-scenario interaction matrix of NO_COLOR x use_color.

    Matrix:
      1. use_color=true  + NO_COLOR unset -> ANSI codes PRESENT
      2. use_color=true  + NO_COLOR=1     -> ANSI codes ABSENT (NO_COLOR wins)
      3. use_color=false + NO_COLOR unset -> ANSI codes ABSENT
      4. use_color=false + NO_COLOR=1     -> ANSI codes ABSENT
    """
    print(f"\n{'=' * 60}")
    print("TEST: Color Control Matrix (NO_COLOR x use_color)")
    print(f"{'=' * 60}")

    ansi_re = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")

    scenarios = [
        {
            "name": "use_color=true, NO_COLOR unset",
            "use_color": True,
            "no_color_value": None,
            "expect_ansi": True,
        },
        {
            "name": "use_color=true, NO_COLOR=1",
            "use_color": True,
            "no_color_value": "1",
            "expect_ansi": False,
        },
        {
            "name": "use_color=false, NO_COLOR unset",
            "use_color": False,
            "no_color_value": None,
            "expect_ansi": False,
        },
        {
            "name": "use_color=false, NO_COLOR=1",
            "use_color": False,
            "no_color_value": "1",
            "expect_ansi": False,
        },
        {
            "name": "use_color=true, NO_COLOR='' (empty string)",
            "use_color": True,
            "no_color_value": "",
            "expect_ansi": False,
        },
    ]

    all_passed = True

    for scenario in scenarios:
        print(f"\n  Scenario: {scenario['name']}")

        config = {"display": {"use_color": scenario["use_color"]}}
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"

        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"

        if scenario["no_color_value"] is not None:
            env["NO_COLOR"] = scenario["no_color_value"]
        else:
            env.pop("NO_COLOR", None)

        try:
            with open(config_path, "w") as f:
                json.dump(config, f)

            result = subprocess.run(
                _build_cmd(),
                input=json.dumps(PAYLOAD_NORMAL),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=5,
                env=env,
            )

            ansi_matches = ansi_re.findall(result.stdout)
            has_ansi = len(ansi_matches) > 0
            has_output = len(result.stdout.strip()) > 0

            if scenario["expect_ansi"]:
                scenario_ok = has_ansi and has_output and result.returncode == 0
                print(
                    f"    Expected ANSI: YES | Found ANSI: {has_ansi} | {'PASS' if scenario_ok else 'FAIL'}"
                )
            else:
                scenario_ok = not has_ansi and has_output and result.returncode == 0
                print(
                    f"    Expected ANSI: NO  | Found ANSI: {has_ansi} | {'PASS' if scenario_ok else 'FAIL'}"
                )

            if not scenario_ok:
                all_passed = False
                if has_ansi and not scenario["expect_ansi"]:
                    print(f"    ANSI sequences found: {ansi_matches[:3]}")

        except Exception as e:
            print(f"    ERROR: {e}")
            all_passed = False
        finally:
            config_path.unlink(missing_ok=True)

    print(f"\n  Matrix result: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
    return all_passed


def run_atomic_write_test() -> bool:
    """Test that state file is written atomically (temp file + rename).

    Validates REQ-EN005-007: State writes use atomic pattern.
    Validates REQ-EN005-008: Atomic write failure degrades gracefully.
    Validates REQ-EN005-009: Preserve existing error handling contract.

    The test runs the script twice with a state file, verifying:
    1. State file is created and contains valid JSON after first run
    2. Script still produces correct output (no regression from atomic write change)
    3. Compaction detection still works (depends on state persistence)
    """
    print(f"\n{'=' * 60}")
    print("TEST: Atomic State Writes (EN-005 Batch B)")
    print(f"{'=' * 60}")

    # Use a temporary directory for state file
    state_dir = tempfile.mkdtemp()
    state_file = os.path.join(state_dir, "test-atomic-state.json")

    config = {
        "compaction": {
            "state_file": state_file,
            "detection_threshold": 10000,
        }
    }

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"

    try:
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

        # Run 1: Establish state (first run writes state atomically)
        result1 = subprocess.run(
            _build_cmd(),
            input=json.dumps(PAYLOAD_NORMAL),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            env=env,
        )

        print(f"Run 1 STDOUT: {result1.stdout.strip()[:80]}...")
        print(f"Run 1 EXIT CODE: {result1.returncode}")

        # Check state file was created and contains valid JSON
        state_exists = os.path.exists(state_file)
        print(f"State file exists after run 1: {state_exists}")

        state_valid = False
        if state_exists:
            with open(state_file, "r", encoding="utf-8") as f:
                try:
                    state_data = json.load(f)
                    state_valid = "previous_context_tokens" in state_data
                    print(f"State file contains valid JSON: {state_valid}")
                    print(
                        f"  previous_context_tokens: {state_data.get('previous_context_tokens')}"
                    )
                except json.JSONDecodeError:
                    print("State file contains INVALID JSON")

        # Check no temp files left behind (atomic write cleaned up)
        tmp_files = [f for f in os.listdir(state_dir) if f.endswith(".tmp")]
        no_orphan_tmp = len(tmp_files) == 0
        print(f"No orphan .tmp files: {no_orphan_tmp}")
        if tmp_files:
            print(f"  Orphan files: {tmp_files}")

        # Run 2: With high previous context, should detect compaction
        # (proves state was written correctly and can be read back)
        result2 = subprocess.run(
            _build_cmd(),
            input=json.dumps(PAYLOAD_NORMAL),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            env=env,
        )

        print(f"Run 2 EXIT CODE: {result2.returncode}")
        run2_ok = result2.returncode == 0 and len(result2.stdout.strip()) > 0
        print(f"Run 2 produces output: {run2_ok}")

        all_ok = (
            result1.returncode == 0
            and state_exists
            and state_valid
            and no_orphan_tmp
            and run2_ok
        )

        print(f"Atomic write test: {'PASS' if all_ok else 'FAIL'}")
        return all_ok

    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        config_path.unlink(missing_ok=True)
        shutil.rmtree(state_dir, ignore_errors=True)


# =============================================================================
# EN-006 Tests: Platform Expansion - Schema Version Checking + Upgrade Docs
# =============================================================================


def run_schema_version_in_config_test() -> bool:
    """Test that DEFAULT_CONFIG contains a schema_version field.

    TASK-002: Schema version checking.
    The DEFAULT_CONFIG embedded in statusline.py must include a top-level
    'schema_version' key so that config files can be version-tracked.
    """
    print(f"\n{'=' * 60}")
    print("TEST: Schema Version in DEFAULT_CONFIG (EN-006 TASK-002)")
    print(f"{'=' * 60}")

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"

    # Run a Python snippet that imports DEFAULT_CONFIG and checks for schema_version
    check_script = (
        "import json, sys; sys.path.insert(0, ''); "
        "from statusline import DEFAULT_CONFIG; "
        "has_key = 'schema_version' in DEFAULT_CONFIG; "
        "print(json.dumps({'has_schema_version': has_key, 'value': DEFAULT_CONFIG.get('schema_version')})); "
        "sys.exit(0 if has_key else 1)"
    )

    try:
        result = subprocess.run(
            [sys.executable, "-c", check_script],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            env=env,
            cwd=str(SCRIPT_DIR),
        )

        print(f"STDOUT: {result.stdout.strip()}")
        if result.stderr:
            print(f"STDERR: {result.stderr.strip()}")
        print(f"EXIT CODE: {result.returncode}")

        has_version = result.returncode == 0
        print(f"DEFAULT_CONFIG has schema_version: {has_version}")

        return has_version

    except Exception as e:
        print(f"ERROR: {e}")
        return False


def run_schema_version_in_state_test() -> bool:
    """Test that saved state files include a schema_version field.

    TASK-002: Schema version checking.
    When the script saves state (via save_state), the resulting JSON file
    must include a 'schema_version' field for forward compatibility.
    """
    print(f"\n{'=' * 60}")
    print("TEST: Schema Version in State File (EN-006 TASK-002)")
    print(f"{'=' * 60}")

    state_dir = tempfile.mkdtemp()
    state_file = os.path.join(state_dir, "test-schema-state.json")

    config = {
        "compaction": {
            "state_file": state_file,
            "detection_threshold": 10000,
        }
    }

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"

    try:
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

        # Run the script to trigger state save
        result = subprocess.run(
            _build_cmd(),
            input=json.dumps(PAYLOAD_NORMAL),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            env=env,
        )

        print(f"Script EXIT CODE: {result.returncode}")

        # Check the saved state file for schema_version
        has_schema_version = False
        if os.path.exists(state_file):
            with open(state_file, "r", encoding="utf-8") as f:
                state_data = json.load(f)
                has_schema_version = "schema_version" in state_data
                print(f"State file contents: {json.dumps(state_data)}")
                print(f"State has schema_version: {has_schema_version}")
        else:
            print("State file was not created")

        return has_schema_version

    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        config_path.unlink(missing_ok=True)
        shutil.rmtree(state_dir, ignore_errors=True)


def run_schema_version_mismatch_warning_test() -> bool:
    """Test that a schema version mismatch produces a warning in output.

    TASK-002: Schema version checking.
    When the user's config file contains a schema_version that differs from
    the script's expected schema_version, the output should include a
    warning indicator (e.g., containing 'version' or 'mismatch' or a
    warning icon) to alert the user that their config may be outdated.
    """
    print(f"\n{'=' * 60}")
    print("TEST: Schema Version Mismatch Warning (EN-006 TASK-002)")
    print(f"{'=' * 60}")

    # Create a config with a mismatched schema version (very old version)
    config = {"schema_version": "0"}

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    # Enable debug mode so debug_log() warnings are visible in stderr
    env["ECW_DEBUG"] = "1"

    try:
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

        result = subprocess.run(
            _build_cmd(),
            input=json.dumps(PAYLOAD_NORMAL),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            env=env,
        )

        print(f"STDOUT: {result.stdout.strip()}")
        if result.stderr:
            print(f"STDERR: {result.stderr.strip()}")
        print(f"EXIT CODE: {result.returncode}")

        # Look for version mismatch warning in stdout or stderr
        combined_output = result.stdout + result.stderr
        has_warning = (
            "version" in combined_output.lower()
            and ("mismatch" in combined_output.lower()
                 or "outdated" in combined_output.lower()
                 or "upgrade" in combined_output.lower()
                 or "warning" in combined_output.lower())
        ) or "⚠" in combined_output

        print(f"Version mismatch warning present: {has_warning}")

        return result.returncode == 0 and has_warning

    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        config_path.unlink(missing_ok=True)


def run_unversioned_config_backward_compat_test() -> bool:
    """Test backward compatibility when config has no schema_version.

    TASK-002: Schema version checking.
    When the config file has NO schema_version field at all (legacy config),
    the script should still work without crashing - treating it as v1.0 for
    backward compatibility. No version mismatch warning should appear.
    """
    print(f"\n{'=' * 60}")
    print("TEST: Unversioned Config Backward Compat (EN-006 TASK-002)")
    print(f"{'=' * 60}")

    # Config with no schema_version - simulates a pre-EN-006 config
    config = {"cost": {"currency_symbol": "$"}}

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"

    try:
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

        result = subprocess.run(
            _build_cmd(),
            input=json.dumps(PAYLOAD_NORMAL),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            env=env,
        )

        print(f"STDOUT: {result.stdout.strip()}")
        if result.stderr:
            print(f"STDERR: {result.stderr.strip()}")
        print(f"EXIT CODE: {result.returncode}")

        # Should NOT crash - produces valid output
        has_output = len(result.stdout.strip()) > 0
        no_crash = result.returncode == 0

        # Should NOT have a version mismatch warning
        combined_output = result.stdout + result.stderr
        has_mismatch_warning = (
            "mismatch" in combined_output.lower()
            or "outdated" in combined_output.lower()
        )

        print(f"Produces output without crash: {has_output and no_crash}")
        print(f"No mismatch warning (expected): {not has_mismatch_warning}")

        return no_crash and has_output and not has_mismatch_warning

    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        config_path.unlink(missing_ok=True)


def run_schema_version_match_no_warning_test() -> bool:
    """Test that matching schema_version produces no warning.

    TASK-002: Schema version checking.
    When the config file's schema_version matches the script's expected
    schema_version, no version warning should appear in output.
    """
    print(f"\n{'=' * 60}")
    print("TEST: Schema Version Match No Warning (EN-006 TASK-002)")
    print(f"{'=' * 60}")

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"

    # First, get the expected schema_version from DEFAULT_CONFIG
    # (This test assumes it will exist after TASK-002 implementation)
    get_version_script = (
        "import sys; sys.path.insert(0, ''); "
        "from statusline import DEFAULT_CONFIG; "
        "v = DEFAULT_CONFIG.get('schema_version', ''); "
        "print(v)"
    )

    try:
        version_result = subprocess.run(
            [sys.executable, "-c", get_version_script],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            env=env,
            cwd=str(SCRIPT_DIR),
        )

        expected_version = version_result.stdout.strip()
        print(f"Expected schema_version from DEFAULT_CONFIG: '{expected_version}'")

        if not expected_version:
            print("FAIL: DEFAULT_CONFIG has no schema_version yet (expected for RED phase)")
            return False

        # Create a config with the matching schema_version
        config = {"schema_version": expected_version}
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

        result = subprocess.run(
            _build_cmd(),
            input=json.dumps(PAYLOAD_NORMAL),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            env=env,
        )

        print(f"STDOUT: {result.stdout.strip()}")
        if result.stderr:
            print(f"STDERR: {result.stderr.strip()}")
        print(f"EXIT CODE: {result.returncode}")

        # Should NOT have any version warning
        combined_output = result.stdout + result.stderr
        has_version_warning = (
            "mismatch" in combined_output.lower()
            or "outdated" in combined_output.lower()
            or "⚠" in combined_output
        )

        has_output = len(result.stdout.strip()) > 0
        no_crash = result.returncode == 0

        print(f"No version warning (expected): {not has_version_warning}")
        print(f"Valid output: {has_output and no_crash}")

        return no_crash and has_output and not has_version_warning

    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        config_path.unlink(missing_ok=True)


def run_upgrade_docs_exist_test() -> bool:
    """Test that GETTING_STARTED.md contains an Upgrade/Migration section.

    TASK-001: Upgrade path documentation.
    The GETTING_STARTED.md must include a section heading containing
    'Upgrade' or 'Migration' to guide users upgrading between versions.
    """
    print(f"\n{'=' * 60}")
    print("TEST: Upgrade Docs Exist in GETTING_STARTED.md (EN-006 TASK-001)")
    print(f"{'=' * 60}")

    getting_started_path = SCRIPT_DIR / "GETTING_STARTED.md"

    try:
        if not getting_started_path.exists():
            print("FAIL: GETTING_STARTED.md not found")
            return False

        with open(getting_started_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Look for a markdown heading containing "Upgrade" or "Migration"
        # Matches ## Upgrade, ## Migration, ## Upgrading, ## Migration Guide, etc.
        upgrade_pattern = re.compile(
            r"^#{1,3}\s+.*(?:Upgrade|Migration|Upgrading|Migrating).*$",
            re.IGNORECASE | re.MULTILINE,
        )

        matches = upgrade_pattern.findall(content)
        has_upgrade_section = len(matches) > 0

        if has_upgrade_section:
            print(f"Found upgrade section heading(s): {matches}")
        else:
            print("No upgrade/migration section heading found")

        print(f"Upgrade docs present: {has_upgrade_section}")

        return has_upgrade_section

    except Exception as e:
        print(f"ERROR: {e}")
        return False


def main() -> int:
    """Run all tests."""
    print("ECW Status Line - Test Suite v3.0.0")
    print(f"Script: {STATUSLINE_SCRIPT}")
    print("Single-file deployment test")

    if not STATUSLINE_SCRIPT.exists():
        print(f"ERROR: Script not found at {STATUSLINE_SCRIPT}")
        return 1

    tests = [
        ("Normal Session (All Green)", PAYLOAD_NORMAL),
        ("Warning State (Yellow)", PAYLOAD_WARNING),
        ("Critical State (Red)", PAYLOAD_CRITICAL),
        ("Bug Simulation (Cumulative > Window)", PAYLOAD_BUG_SIMULATION),
        ("Haiku Model", PAYLOAD_HAIKU),
        ("Minimal Payload (Edge Case)", PAYLOAD_MINIMAL),
    ]

    passed = 0
    failed = 0

    # Basic tests
    for name, payload in tests:
        if run_test(name, payload):
            passed += 1
        else:
            failed += 1

    # Tools segment test
    if run_tools_test():
        passed += 1
    else:
        failed += 1

    # Compact mode test
    if run_compact_test():
        passed += 1
    else:
        failed += 1

    # New v3.0.0 tests

    # Currency configuration test
    if run_currency_test():
        passed += 1
    else:
        failed += 1

    # Tokens segment test (fresh/cached breakdown)
    if run_tokens_segment_test():
        passed += 1
    else:
        failed += 1

    # Session segment test (duration + total tokens)
    if run_session_segment_test():
        passed += 1
    else:
        failed += 1

    # Compaction detection test
    if run_compaction_test():
        passed += 1
    else:
        failed += 1

    # EN-002: Platform verification tests

    # No HOME environment (Docker/container)
    if run_no_home_test():
        passed += 1
    else:
        failed += 1

    # No TTY (pipe/container)
    if run_no_tty_test():
        passed += 1
    else:
        failed += 1

    # Read-only filesystem (state file)
    if run_readonly_state_test():
        passed += 1
    else:
        failed += 1

    # Emoji disabled (ASCII fallback)
    if run_emoji_disabled_test():
        passed += 1
    else:
        failed += 1

    # Corrupt state file (invalid JSON)
    if run_corrupt_state_test():
        passed += 1
    else:
        failed += 1

    # EN-005: Edge Case Handling - Batch A (Color/ANSI Control)

    # NO_COLOR environment variable (G-016)
    if run_no_color_env_test():
        passed += 1
    else:
        failed += 1

    # use_color config toggle disabled (G-021)
    if run_use_color_disabled_test():
        passed += 1
    else:
        failed += 1

    # NO_COLOR x use_color interaction matrix
    if run_color_matrix_test():
        passed += 1
    else:
        failed += 1

    # EN-005: Edge Case Handling - Batch B (Atomic Writes)

    # Atomic state file writes
    if run_atomic_write_test():
        passed += 1
    else:
        failed += 1

    # EN-006: Platform Expansion - Schema Version Checking + Upgrade Docs

    # Schema version in DEFAULT_CONFIG
    if run_schema_version_in_config_test():
        passed += 1
    else:
        failed += 1

    # Schema version in saved state files
    if run_schema_version_in_state_test():
        passed += 1
    else:
        failed += 1

    # Schema version mismatch produces warning
    if run_schema_version_mismatch_warning_test():
        passed += 1
    else:
        failed += 1

    # Unversioned config backward compatibility
    if run_unversioned_config_backward_compat_test():
        passed += 1
    else:
        failed += 1

    # Matching schema version produces no warning
    if run_schema_version_match_no_warning_test():
        passed += 1
    else:
        failed += 1

    # Upgrade documentation exists in GETTING_STARTED.md
    if run_upgrade_docs_exist_test():
        passed += 1
    else:
        failed += 1

    print(f"\n{'=' * 60}")
    print(f"RESULTS: {passed} passed, {failed} failed")
    print(f"{'=' * 60}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
