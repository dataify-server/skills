#!/usr/bin/env python3
"""Remove legacy full-parameter confirmation mandates and sync progressive interaction policy."""

import argparse
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "parameter-interaction.json"
TARGETS = "skills/*/SKILL*.md"
EN_SECTION = re.compile(r"\n+## Parameter interaction policy\n.*?(?=\n## |\Z)", re.DOTALL)
ZH_SECTION = re.compile(r"\n+## 参数交互策略\n.*?(?=\n## |\Z)", re.DOTALL)
LEGACY_CONFIRMATION_SECTIONS = (
    re.compile(
        r"\n+## Required Pre-Call Confirmation\n.*?(?=\n## |\Z)",
        re.DOTALL | re.IGNORECASE,
    ),
    re.compile(
        r"\n+## 调用前确认（必须）\n.*?(?=\n## |\Z)",
        re.DOTALL,
    ),
)
LEGACY_PARAMETER_PREVIEW_BLOCK = re.compile(
    r"\n*```(?:bash)?\n(?:(?!```).)*(?:--params-table|preview_params\.py)(?:(?!```).)*```\n*",
    re.DOTALL,
)
LEGACY_LINE_PATTERNS = tuple(re.compile(pattern, re.IGNORECASE) for pattern in (
    r"before every (?:real |live )?api call",
    r"before submitting, show the user",
    r"always display .*parameters?.*markdown table",
    r"when the user invokes this skill, first tell",
    r"then ask:",
    r"after (?:showing )?the table,? ask",
    r"ask the user whether .*modify",
    r"do not call the api until",
    r"show the preview table to the user",
    r"show the table to the user with exactly",
    r"always show a complete field list",
    r"complete (?:request )?field list",
    r"complete request-parameter table",
    r"the table must (?:have|use|include|contain)",
    r"wait for user confirmation",
    r"user confirms? the parameter table",
    r"call the api only after a clear confirmation",
    r"follow this confirmation flow",
    r"present those options back to the user before",
    r"show all .*options .*before asking",
    r"ask whether the user wants to collect multiple parameter sets",
    r"提交前，向用户展示.*必填值",
    r"始终以 markdown 表格展示",
    r"当用户调用此技能时，首先告知",
    r"然后询问",
    r"每次调用 api 前.*表格",
    r"调用 api 前展示 markdown 参数表",
    r"每次实际调用 api 前",
    r"每次真正调用 api 前",
    r"在任何 api 调用前",
    r"展示表格后.*询问用户是否需要修改参数",
    r"询问用户是否需要修改参数",
    r"用户.*确认.*(?:才能|才|后).*调用 api",
    r"用户确认前不要调用 api",
    r"确认预览表格前不要调用 api",
    r"完整字段列表",
    r"完整的请求参数表格",
    r"表格必须(?:恰好)?包含",
    r"表格只能包含",
    r"向用户展示表格，恰好包含",
    r"仅在用户确认表格后",
    r"不要调用 api，?直到用户确认",
    r"使用.*预览.*生成确认表格",
    r"生成确认表格",
    r"在实际调用前生成确认表格",
    r"先把选项展示给用户，再生成最终请求",
    r"询问用户是否要采集多个",
    r"--confirmed",
    r"除非 api 有文档化的默认值需要在确认表格中显示",
))


def policy_sections():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    en = "## Parameter interaction policy\n\n" + "\n".join("- " + item for item in config["policy_en"])
    zh = "## 参数交互策略\n\n" + "\n".join("- " + item for item in config["policy_zh"])
    return en, zh


def remove_legacy_mandates(text):
    for pattern in LEGACY_CONFIRMATION_SECTIONS:
        text = pattern.sub("", text)
    text = LEGACY_PARAMETER_PREVIEW_BLOCK.sub("\n", text)
    kept = []
    for line in text.splitlines():
        if any(pattern.search(line) for pattern in LEGACY_LINE_PATTERNS):
            continue
        line = re.sub(
            r"如果用户未提供，仅在参数确认表格中展示后(?:才)?使用[^。]*默认值[^。]*。",
            "如果用户未提供，询问该必填值；不要使用文档示例值代替用户输入。",
            line,
        )
        line = line.replace("预览完整的参数表格", "按需预览高级参数")
        line = line.replace("预览确认表格", "按需预览高级参数")
        line = line.replace("所需确认表格", "高级参数")
        line = line.replace(
            "如果用户未提供，仅在参数确认表格中展示后使用默认帖子 URL。",
            "如果用户未提供，询问帖子 URL；不要使用文档示例值代替用户输入。",
        )
        line = line.replace(
            "apply their changes and show the full table again",
            "apply their changes and show only consequential changed values when a recap is useful",
        )
        line = line.replace(
            "update the current values and show the full table again. Call the API only after a clear confirmation such as \"确认\", \"可以\", \"调用\", \"继续\", \"yes\", or equivalent.",
            "update the current values and recap only consequential changed values when useful.",
        )
        kept.append(line)
    return "\n".join(kept).rstrip() + "\n"


def insert_policy(text, section, chinese=False):
    text = (ZH_SECTION if chinese else EN_SECTION).sub("", text).rstrip()
    marker = "\n## Account CTA policy"
    if marker in text:
        before, after = text.split(marker, 1)
        return before.rstrip() + "\n\n" + section + "\n\n## Account CTA policy" + after.rstrip() + "\n"
    return text + "\n\n" + section + "\n"


def synchronize(check=False):
    en, zh = policy_sections()
    changed = []
    for path in sorted(ROOT.glob(TARGETS)):
        text = path.read_text(encoding="utf-8")
        updated = remove_legacy_mandates(text)
        updated = insert_policy(updated, zh if path.name.endswith("zh-CN.md") else en, path.name.endswith("zh-CN.md"))
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
    parser.add_argument("--check", action="store_true", help="Fail when generated interaction policy is stale.")
    args = parser.parse_args()
    return synchronize(args.check)


if __name__ == "__main__":
    raise SystemExit(main())
