#!/usr/bin/env python3
"""
ECW Status Line - Test Suite
Validates statusline output with mock Claude Code JSON payloads.

Version: 2.0.0
Usage: python3 test_statusline.py
"""

import json
import os
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

# =============================================================================
# TRANSCRIPT TEST DATA
# =============================================================================

SAMPLE_TRANSCRIPT = [
    {
        "message": {
            "role": "assistant",
            "content": [
                {"type": "tool_use", "name": "Read", "input": {"file_path": "/test.py" * 100}},
            ],
        }
    },
    {
        "message": {
            "role": "assistant",
            "content": [
                {"type": "tool_use", "name": "Read", "input": {"file_path": "/other.py" * 50}},
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


def run_test(name: str, payload: dict, config_override: dict = None) -> bool:
    """Run statusline script with payload and display result."""
    print(f"\n{'=' * 60}")
    print(f"TEST: {name}")
    print(f"{'=' * 60}")

    env = os.environ.copy()

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
            ["python3", str(STATUSLINE_SCRIPT)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
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
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False
    ) as tf:
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
            ["python3", str(STATUSLINE_SCRIPT)],
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
    """Test compact mode."""
    print(f"\n{'=' * 60}")
    print("TEST: Compact Mode")
    print(f"{'=' * 60}")

    config = {"display": {"compact_mode": True}}

    try:
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

        result = subprocess.run(
            ["python3", str(STATUSLINE_SCRIPT)],
            input=json.dumps(PAYLOAD_NORMAL),
            capture_output=True,
            text=True,
            timeout=5,
        )

        print(f"STDOUT: {result.stdout.strip()}")

        # Compact mode should NOT have session or directory
        has_session = "⏱️" in result.stdout
        has_directory = "📂" in result.stdout

        print(f"Session hidden (expected): {not has_session}")
        print(f"Directory hidden (expected): {not has_directory}")

        return result.returncode == 0 and not has_session and not has_directory

    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        config_path = SCRIPT_DIR / "ecw-statusline-config.json"
        config_path.unlink(missing_ok=True)


def main() -> int:
    """Run all tests."""
    print("ECW Status Line - Test Suite v2.0.0")
    print(f"Script: {STATUSLINE_SCRIPT}")
    print(f"Single-file deployment test")

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

    print(f"\n{'=' * 60}")
    print(f"RESULTS: {passed} passed, {failed} failed")
    print(f"{'=' * 60}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
