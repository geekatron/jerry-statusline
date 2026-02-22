#!/usr/bin/env python3

"""Validate and synchronize ECW Status Line version across all locations.

This script reads the SSOT version from pyproject.toml and checks (or fixes)
all other version locations for consistency.

Usage:
    python3 scripts/sync_versions.py --check   # CI: validate consistency
    python3 scripts/sync_versions.py --fix      # Developer: force-sync all files

Exit codes:
    0: All versions consistent (--check) or sync successful (--fix)
    1: Version drift detected (--check) or sync failed (--fix)

Version locations:
    - pyproject.toml: SSOT (project.version + tool.bumpversion.current_version)
    - statusline.py: __version__ string
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def read_ssot_version(project_root: Path) -> str:
    """Read the authoritative version from pyproject.toml [project] section."""
    pyproject = project_root / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if not match:
        print("ERROR: Could not find version in pyproject.toml")
        sys.exit(1)
    return match.group(1)


def check_statusline_version(
    project_root: Path, expected: str
) -> tuple[bool, str]:
    """Check statusline.py __version__ string."""
    path = project_root / "statusline.py"
    content = path.read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if not match:
        return False, "statusline.py: __version__ not found"
    actual = match.group(1)
    ok = actual == expected
    return ok, f"statusline.py: {actual}" + ("" if ok else f" (expected {expected})")


def fix_statusline_version(project_root: Path, version: str) -> None:
    """Fix statusline.py __version__ string."""
    path = project_root / "statusline.py"
    content = path.read_text(encoding="utf-8")
    new_content = re.sub(
        r'^(__version__\s*=\s*")[^"]+"',
        rf'\g<1>{version}"',
        content,
        count=1,
        flags=re.MULTILINE,
    )
    path.write_text(new_content, encoding="utf-8")


def main() -> int:
    """Run version sync check or fix."""
    if len(sys.argv) < 2 or sys.argv[1] not in ("--check", "--fix"):
        print("Usage: sync_versions.py [--check | --fix]")
        return 1

    mode = sys.argv[1]
    project_root = get_project_root()
    expected = read_ssot_version(project_root)

    print(f"SSOT version (pyproject.toml): {expected}")
    print(f"Mode: {mode}")
    print()

    if mode == "--check":
        all_ok = True
        checks = [
            check_statusline_version(project_root, expected),
        ]

        for ok, msg in checks:
            status = "OK" if ok else "DRIFT"
            print(f"  [{status}] {msg}")
            if not ok:
                all_ok = False

        print()
        if all_ok:
            print("All versions consistent.")
            return 0
        else:
            print("ERROR: Version drift detected!")
            print("Run: python3 scripts/sync_versions.py --fix")
            return 1

    elif mode == "--fix":
        print(f"Syncing all files to version {expected}...")
        fix_statusline_version(project_root, expected)
        print("Done. All files synced.")
        print()
        print("Don't forget to stage the changes:")
        print("  git add statusline.py")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
