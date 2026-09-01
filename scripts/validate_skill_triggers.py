#!/usr/bin/env python3
"""Validate Dataify Skill trigger descriptions and routing-case coverage."""

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "config" / "skill-trigger-cases.json"
MAX_DESCRIPTION_LENGTH = 500
FORBIDDEN_INTERNAL_PHRASES = (
    "successful Dataify scraper detail entry",
    "getToolParams",
    "DATAIFY_API_TOKEN",
    "task_id",
    "task status",
    "troubleshoot",
)
BOUNDARY_SKILLS = {
    "dataify-youtube-video-by-url",
    "dataify-youtube-video-post",
    "dataify-youtube-product-by-id",
    "dataify-google-maps",
    "dataify-google-map-details",
    "dataify-google-shopping",
    "dataify-google-shopping-keywords",
    "dataify-amazon-product",
    "dataify-amazon-product-list",
    "dataify-amazon-global-product",
}


def frontmatter_value(text, key):
    match = re.search(r"^{}:\s*(.+)$".format(re.escape(key)), text, re.MULTILINE)
    if not match:
        raise ValueError("missing {}".format(key))
    raw = match.group(1).strip()
    if raw.startswith('"'):
        return json.loads(raw)
    return raw.strip("'")


def descriptions():
    result = {}
    for path in sorted(ROOT.glob("skills/*/SKILL.md")):
        text = path.read_text(encoding="utf-8")
        result[frontmatter_value(text, "name")] = (frontmatter_value(text, "description"), path)
    return result


def validate():
    errors = []
    current = descriptions()
    for name, (description, path) in current.items():
        if len(description) > MAX_DESCRIPTION_LENGTH:
            errors.append("{}: description is {} characters (max {})".format(path, len(description), MAX_DESCRIPTION_LENGTH))
        is_business_skill = name not in {
            "dataify-router", "dataify-task-operations", "dataify-task-status", "dataify-task-result"
        }
        for phrase in FORBIDDEN_INTERNAL_PHRASES:
            if is_business_skill and phrase.lower() in description.lower():
                errors.append("{}: contains internal trigger phrase {!r}".format(path, phrase))
        if name in BOUNDARY_SKILLS and "Do not use" not in description:
            errors.append("{}: missing adjacent-skill boundary".format(path))

    shopping = current.get("dataify-google-shopping-keywords", ("", None))[0].lower()
    for contaminant in ("instagram", "reel"):
        if contaminant in shopping:
            errors.append("dataify-google-shopping-keywords: contains contaminant {!r}".format(contaminant))

    dataset = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    cases = dataset.get("cases", [])
    if len(cases) < 18:
        errors.append("trigger case dataset must contain at least 18 cases")
    positive_counts = {}
    negative_counts = {}
    for index, case in enumerate(cases):
        expected = case.get("expected")
        forbidden = case.get("forbidden") or []
        if expected not in current:
            errors.append("case {}: unknown expected skill {}".format(index, expected))
        positive_counts[expected] = positive_counts.get(expected, 0) + 1
        if not forbidden:
            errors.append("case {}: forbidden list is empty".format(index))
        for name in forbidden:
            if name not in current:
                errors.append("case {}: unknown forbidden skill {}".format(index, name))
            negative_counts[name] = negative_counts.get(name, 0) + 1

    for name in BOUNDARY_SKILLS:
        if not positive_counts.get(name):
            errors.append("{}: no positive routing case".format(name))
        if not negative_counts.get(name):
            errors.append("{}: no negative routing case".format(name))
    return errors


def main():
    errors = validate()
    if errors:
        for error in errors:
            print(error)
        return 1
    print("OK: validated trigger descriptions and routing cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
