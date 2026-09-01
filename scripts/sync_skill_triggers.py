#!/usr/bin/env python3
"""Synchronize Skill frontmatter descriptions from the trigger registry."""

import argparse
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config" / "skill-trigger-descriptions.json"
DESCRIPTION_PATTERN = re.compile(r"^description:.*$", re.MULTILINE)


def load_registry():
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not data:
        raise ValueError("trigger description registry must be a non-empty object")
    return data


def skill_files():
    return sorted(ROOT.glob("skills/*/SKILL.md"))


def synchronize(check=False):
    registry = load_registry()
    files = skill_files()
    folders = {path.parent.name for path in files}
    missing = sorted(folders - set(registry))
    extra = sorted(set(registry) - folders)
    if missing or extra:
        if missing:
            print("missing registry entries: {}".format(", ".join(missing)), file=sys.stderr)
        if extra:
            print("unknown registry entries: {}".format(", ".join(extra)), file=sys.stderr)
        return 2

    changed = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        replacement = "description: " + json.dumps(registry[path.parent.name], ensure_ascii=False)
        updated, count = DESCRIPTION_PATTERN.subn(replacement, text, count=1)
        if count != 1:
            print("description field missing: {}".format(path.relative_to(ROOT)), file=sys.stderr)
            return 2
        if updated != text:
            changed.append(path)
            if not check:
                path.write_text(updated, encoding="utf-8")

    if check and changed:
        for path in changed:
            print(path.relative_to(ROOT), file=sys.stderr)
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail when Skill descriptions are stale.")
    args = parser.parse_args()
    return synchronize(args.check)


if __name__ == "__main__":
    raise SystemExit(main())
