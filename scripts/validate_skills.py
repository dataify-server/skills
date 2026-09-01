#!/usr/bin/env python3
"""Validate Dataify skill structure and local references without network access."""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path


LOCAL_REF = re.compile(r"(?<![\w.-])((?:scripts|references)/[A-Za-z0-9_.*-]+(?:/[A-Za-z0-9_.*-]+)*)")
NAME = re.compile(r"^[a-z0-9-]{1,64}$")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    skill_files = sorted((root / "skills").glob("*/SKILL.md"))
    if not skill_files:
        return ["no skills/*/SKILL.md files found"]

    names: dict[str, Path] = {}
    for path in skill_files:
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            errors.append(f"{path}: UTF-8 BOM before frontmatter")
        text = raw.decode("utf-8-sig")
        match = re.match(r"^---\n(.*?)\n---(?:\n|$)", text, re.DOTALL)
        if not match:
            errors.append(f"{path}: missing YAML frontmatter")
            continue
        frontmatter = match.group(1)
        name_match = re.search(r"^name:\s*[\"']?([^\"'\n]+)", frontmatter, re.MULTILINE)
        desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
        if not name_match or not desc_match:
            errors.append(f"{path}: frontmatter requires name and description")
        else:
            name = name_match.group(1).strip()
            if not NAME.fullmatch(name):
                errors.append(f"{path}: invalid skill name {name!r}")
            if name in names:
                errors.append(f"{path}: duplicate name also used by {names[name]}")
            names[name] = path

        for ref in sorted(set(LOCAL_REF.findall(text))):
            matches = list(path.parent.glob(ref)) if "*" in ref else [path.parent / ref]
            if not matches or any(not candidate.exists() for candidate in matches):
                errors.append(f"{path}: missing local reference {ref}")

    for script in sorted((root / "skills").glob("*/scripts/*.py")):
        try:
            ast.parse(script.read_text(encoding="utf-8-sig"), filename=str(script))
        except SyntaxError as exc:
            errors.append(f"{script}:{exc.lineno}: Python syntax error: {exc.msg}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        print("\n".join(f"ERROR {error}" for error in errors))
        return 1
    count = len(list((args.root.resolve() / "skills").glob("*/SKILL.md")))
    print(f"OK: validated {count} skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())

