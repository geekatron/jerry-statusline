#!/usr/bin/env python3
"""
ECW Status Line - Test Suite
Validates statusline output with mock Claude Code JSON payloads.

Usage:
    python3 test_statusline.py
"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
STATUSLINE_SCRIPT = SCRIPT_DIR / "statusline.py"

# =============================================================================
# TEST PAYLOADS
# =============================================================================

# Normal session - all green
PAYLOAD_NORMAL = {
    "hook_event_name": "Status",
    "session_id": "test-session-001",
    "transcript_path": "/tmp/transcript.json",
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
        "total_duration_ms": 300000,  # 5 minutes
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
            "cache_read_input_tokens": 12000,  # High cache hit
        },
    },
    "exceeds_200k_tokens": False,
}

# Warning state - context at 70%, moderate cost
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
        "total_duration_ms": 7200000,  # 2 hours
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
            "cache_read_input_tokens": 5000,  # Low cache hit
        },
    },
}

# Critical state - high context, high cost
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
        "total_duration_ms": 14400000,  # 4 hours
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
            "cache_read_input_tokens": 1000,  # Very low cache hit
        },
    },
}

# Bug simulation - cumulative tokens exceed context window
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
        "total_duration_ms": 18000000,  # 5 hours
    },
    "context_window": {
        "total_input_tokens": 340000,  # Exceeds 200k!
        "total_output_tokens": 100000,
        "context_window_size": 200000,
        # current_usage is null (simulating old data or missing field)
    },
}

# Haiku model test
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
        "total_duration_ms": 60000,  # 1 minute
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

# Minimal payload (edge case)
PAYLOAD_MINIMAL = {
    "model": {"display_name": "Unknown"},
    "workspace": {},
    "cost": {},
    "context_window": {},
}

# =============================================================================
# TEST RUNNER
# =============================================================================


def run_test(name: str, payload: dict) -> bool:
    """Run statusline script with payload and display result."""
    print(f"\n{'=' * 60}")
    print(f"TEST: {name}")
    print(f"{'=' * 60}")

    try:
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

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("ERROR: Script timed out!")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def main() -> int:
    """Run all tests."""
    print("ECW Status Line - Test Suite")
    print(f"Script: {STATUSLINE_SCRIPT}")

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

    for name, payload in tests:
        if run_test(name, payload):
            passed += 1
        else:
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"RESULTS: {passed} passed, {failed} failed")
    print(f"{'=' * 60}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
