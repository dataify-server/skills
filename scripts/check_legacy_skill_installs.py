#!/usr/bin/env python3
"""Detect stale skill folders that declare the same name as a canonical skill."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def skill_name(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError):
        return None
    match = re.search(r'^name:\s*["\']?([^"\'\r\n]+)', text, re.MULTILINE)
    return match.group(1).strip() if match else None


def canonical_names(skills_dir: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in skills_dir.glob("*/SKILL.md"):
        name = skill_name(path)
        if name:
            result[name] = path.parent.name
    return result


def conflicts(skills_dir: Path, installed_dirs: list[Path]) -> list[tuple[Path, str, str]]:
    canonical = canonical_names(skills_dir)
    found: list[tuple[Path, str, str]] = []
    for installed_dir in installed_dirs:
        if not installed_dir.is_dir():
            continue
        for path in installed_dir.glob("*/SKILL.md"):
            name = skill_name(path)
            expected_folder = canonical.get(name or "")
            if expected_folder and path.parent.name != expected_folder:
                found.append((path.parent, name or "", expected_folder))
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-dir", type=Path, required=True)
    parser.add_argument("--installed-dir", action="append", type=Path, default=[])
    args = parser.parse_args()
    found = conflicts(args.skills_dir, args.installed_dir)
    for folder, name, expected in found:
        print(f"Legacy skill folder {folder} declares {name!r}; current folder is {expected!r}.")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
