#!/usr/bin/env python3
"""Migrate Dataify skills to the shared execution and user-facing UX contract."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
CATALOG_WRAPPER = '''#!/usr/bin/env python3
import os
import sys

TASK_RUNTIME_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "dataify-task-operations", "scripts"))
if TASK_RUNTIME_DIR not in sys.path:
    sys.path.insert(0, TASK_RUNTIME_DIR)

from catalog_builder import build_curl, run_catalog_builder


if __name__ == "__main__":
    raise SystemExit(run_catalog_builder(os.path.dirname(__file__)))
'''

RESULT_SECTION = '''## Result presentation

- Return a compact, user-facing result by default: the most relevant titles, links, and vertical-specific fields, plus a count or truncation note when useful.
- Do not expose transport details, fixed engine fields, task plumbing, or the full response envelope in the ordinary flow.
- Return raw JSON or HTML only when the user explicitly requests raw output.
- Preserve source links and distinguish missing fields from empty values; do not invent data.
'''

ZH_RESULT_SECTION = '''## 结果呈现

- 默认返回精简、可直接使用的结果：最相关的标题、链接和垂类关键字段，并在必要时说明数量或截断情况。
- 普通流程不暴露传输细节、固定引擎字段、任务内部状态或完整响应包装。
- 只有用户明确要求原始输出时才返回 raw JSON 或 HTML。
- 保留来源链接，区分字段缺失与空值，不得编造数据。
'''

LEGACY_SECTIONS = re.compile(
    r"\n+## (?:Parameter Notice|Parameter Preview|Parameter Confirmation|参数预览|参数确认)\n.*?(?=\n## |\Z)",
    re.DOTALL | re.IGNORECASE,
)
TOKEN_PARAGRAPHS = (
    re.compile(r"\n+If the user provided a token.*?```.*?```\n", re.DOTALL | re.IGNORECASE),
    re.compile(r"\n+如果用户在对话中提供了 token.*?```.*?```\n", re.DOTALL | re.IGNORECASE),
)
LEGACY_LINES = tuple(phrase.lower() for phrase in (
    "only after parameter confirmation",
    "do not poll for results after Builder succeeds",
    "ask the user to provide the token",
    "user-provided token",
    "Return the script output directly to the user. Do not summarize",
    "Return the raw API response to the user without summarizing",
    "将脚本输出直接返回给用户。不要对 API 响应进行总结",
    "不要对返回结果进行任何加工处理",
    "if the user provides a token",
    "if no token is provided",
    "if no token is available locally",
    "after the user provides an api token",
    "resolve the dataify token from explicit input",
    "tell the user they need to provide",
    "token was provided in the conversation",
    "use the default only after showing",
    "only after showing it in the parameter confirmation table",
    "generate the confirmation table before a live call",
    "return the api response directly to the user without summarizing",
    "if no token is available",
    "ask the user to input a dataify api token",
    "ask the user to provide a token",
    "provide a token, or log in/register",
    "confirmation table",
    "after confirmation",
    "full request-parameter table",
    "return the api response directly without summarizing",
))

CATALOG_QUICK_STARTS = {
    "scraper-airbnb-product-by-searchurl": (
        "an Airbnb search URL",
        "airbnb_product_by-searchurl",
        '[{"searchurl":"https://www.airbnb.com/s/Paris--France/homes"}]',
    ),
    "scraper-crunchbase-company-by-url": (
        "a Crunchbase company URL",
        "crunchbase_company_by-url",
        '[{"url":"https://www.crunchbase.com/organization/openai"}]',
    ),
    "scraper-github-repository-by-repo-url": (
        "a GitHub repository URL",
        "github_repository_by-repo-url",
        '[{"url":"https://github.com/dataify-server/skills"}]',
    ),
    "scraper-google-play-store-reviews-by-url": (
        "a Google Play app URL",
        "google-play-store_reviews_by-url",
        '[{"url":"https://play.google.com/store/apps/details?id=com.google.android.youtube"}]',
    ),
    "scraper-linkedin-company-information-by-url": (
        "a LinkedIn company URL",
        "linkedin_company_information_by-url",
        '[{"url":"https://www.linkedin.com/company/openai"}]',
    ),
    "scraper-twitter-profile-by-profileurl": (
        "an X/Twitter profile URL",
        "twitter_profile_by-profileurl",
        '[{"profileurl":"https://x.com/OpenAI"}]',
    ),
    "scraper-glassdoor-company-by-url": (
        "a Glassdoor company URL",
        "glassdoor_company_by-url",
        '[{"url":"https://www.glassdoor.com/Overview/Working-at-OpenAI"}]',
    ),
}


def insert_before_policy(text, section):
    marker = "\n## Parameter interaction policy"
    zh_marker = "\n## 参数交互策略"
    target = zh_marker if zh_marker in text else marker
    if target in text:
        before, after = text.split(target, 1)
        return before.rstrip() + "\n\n" + section.rstrip() + "\n" + target + after
    return text.rstrip() + "\n\n" + section.rstrip() + "\n"


def first_command(text, folder):
    match = re.search(r"```(?:bash|powershell)?\n([^`]*?python3 scripts/[^\n]+)", text, re.DOTALL)
    if match:
        command = match.group(1).strip().splitlines()[0]
        if "--token" not in command.lower() and "--preview" not in command.lower():
            return command
    scripts = sorted((folder / "scripts").glob("*.py"))
    if scripts:
        return "python3 scripts/{} --help".format(scripts[0].name)
    return "python3 -c 'print(\"Use this routing skill from your agent request.\")'"


def modernize_doc(path):
    text = path.read_text(encoding="utf-8")
    updated = LEGACY_SECTIONS.sub("", text)
    for pattern in TOKEN_PARAGRAPHS:
        updated = pattern.sub("\n", updated)
    kept = []
    for line in updated.splitlines():
        lower = line.lower()
        if re.fullmatch(r'\s*export\s+dataify_api_token=["\x27](?:your_token|your-token)["\x27]\s*', lower):
            continue
        if any(phrase in lower for phrase in LEGACY_LINES):
            continue
        if "--token" in lower:
            continue
        kept.append(line)
    updated = "\n".join(kept).rstrip() + "\n"

    quick_start = CATALOG_QUICK_STARTS.get(path.parent.name) if path.name == "SKILL.md" else None
    if quick_start:
        input_label, tool_sign, params_json = quick_start
        replacement = (
            "## Quick Start\n\n"
            f"**Input:** {input_label}.\n\n"
            "```bash\n"
            f"python3 scripts/build-dataify-request.py --tool-sign {tool_sign} --params-json '{params_json}'\n"
            "```\n\n"
            "This submits the task, waits for completion, downloads the final result, and returns it. "
            "Add `--no-wait` only when submission-only behavior is requested.\n"
        )
        updated = re.sub(
            r"## Quick Start\n.*?(?=\n## |\Z)",
            replacement.rstrip(),
            updated,
            count=1,
            flags=re.DOTALL,
        ) + ("\n" if updated.endswith("\n") else "")

    chinese = path.name.endswith("zh-CN.md")
    result_heading = "## 结果呈现" if chinese else "## Result presentation"
    if path.parent.name.startswith("serp-") and result_heading not in updated:
        updated = insert_before_policy(updated, ZH_RESULT_SECTION if chinese else RESULT_SECTION)

    if path.name == "SKILL.md" and "## Quick Start" not in updated:
        command = first_command(updated, path.parent)
        quick = "## Quick Start\n\n```bash\n{}\n```\n".format(command)
        updated = insert_before_policy(updated, quick)

    if path.parent.name == "serp-google-local":
        updated = updated.replace(
            "Use this skill to turn a user's Google Local request into a Dataify Scraper API form POST.",
            "Use this skill for Google Local/local pack keyword-and-location business results. Do not use it for map-coordinate browsing, a known Place ID, place details, or reviews.",
        )
    elif path.parent.name == "serp-google-maps":
        updated = updated.replace(
            "# Dataify Google Maps",
            "# Dataify Google Maps\n\nUse this skill for explicit Google Maps searches that need map coordinates, zoom, or map pagination. Use Google Local for local-pack keyword lists, Map Details for a known Place ID, and Maps Reviews for reviews.",
            1,
        )
    elif path.parent.name == "scraper-google-maps-reviews" and "known place reviews" not in updated.lower():
        updated = updated.replace("\n", "\n\nUse this skill only for reviews of a known place URL or identifier. Use Google Maps or Google Local to discover places first.\n", 1)
    if updated != text:
        path.write_text(updated, encoding="utf-8")


def slim_long_skill(path):
    text = path.read_text(encoding="utf-8")
    if len(text.splitlines()) <= 220:
        return
    headings = list(re.finditer(r"^## (.+)$", text, re.MULTILINE))
    movable = []
    for index, match in enumerate(headings):
        title = match.group(1)
        move = (
            title == "Parameter Checklists"
            or title == "Shared Dropdown Options"
            or title.endswith("Mode Parameters")
            or title in {"URL Mode", "Search Filters Mode", "Hashtag Mode", "Podcast URL Mode", "Keyword Mode", "Explore Mode"}
        )
        if move:
            end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
            movable.append((match.start(), end, text[match.start():end].strip()))
    if not movable:
        return
    reference_dir = path.parent / "references"
    reference_dir.mkdir(exist_ok=True)
    reference = reference_dir / "modes-and-parameters.md"
    reference.write_text(
        "# Modes and parameters\n\nRead this reference only when selecting a non-default mode or mapping advanced fields.\n\n"
        + "\n\n".join(item[2] for item in movable)
        + "\n",
        encoding="utf-8",
    )
    for start, end, _ in reversed(movable):
        text = text[:start] + text[end:]
    note = "\nFor detailed mode schemas and advanced fields, read [references/modes-and-parameters.md](references/modes-and-parameters.md) only when needed.\n"
    marker = "\n## Dataify Builder Request"
    if note.strip() not in text:
        text = text.replace(marker, note + marker, 1) if marker in text else text + note
    path.write_text(re.sub(r"\n{3,}", "\n\n", text).rstrip() + "\n", encoding="utf-8")


def remove_example_fallbacks(path):
    text = path.read_text(encoding="utf-8")
    updated = text
    target_names = r"DEFAULT_[A-Z_]+(?:\[[^\]]+\])?\b"
    updated = re.sub(r'\.get\(("(?:url|category_url|keyword|keywords|video_id|posturl|profileurl|keyword_search|username|sku|CID|place_id|hashtag)"),\s*' + target_names + r"\)", r".get(\1)", updated)
    updated = re.sub(r"\s+or \[(" + target_names + r")\]", " or []", updated)
    updated = re.sub(r"\s+or (" + target_names + r")", "", updated)
    argument_target_names = r"DEFAULT_(?:[A-Z_]*URLS?|[A-Z_]*KEYWORDS?|VIDEO_ID|POSTURL|PROFILEURL|USERNAME|SKU)\b"
    updated = re.sub(r"(add_argument\([^\n]*?),\s*default=(" + argument_target_names + r")", r"\1", updated)
    if "DEFAULT_FILE_NAME" in updated:
        updated = re.sub(
            r'add_argument\("--file-name",(?!\s*default=)\s*',
            'add_argument("--file-name", default=DEFAULT_FILE_NAME, ',
            updated,
        )
        updated = updated.replace(
            'add_argument("--file-name", default=DEFAULT_FILE_NAME,  default=DEFAULT_FILE_NAME,',
            'add_argument("--file-name", default=DEFAULT_FILE_NAME,',
        )
    updated = re.sub(
        r'^(\s*)groups = build_groups\(([^\n]+)\)\n(?!\1if not groups:)',
        r'\1groups = build_groups(\2)\n\1if not groups:\n\1    raise ValueError("At least one business target is required.")\n',
        updated,
        flags=re.MULTILINE,
    )
    if updated != text:
        path.write_text(updated, encoding="utf-8")


def main():
    for wrapper in SKILLS.glob("scraper-*/scripts/build-dataify-request.py"):
        wrapper.write_text(CATALOG_WRAPPER, encoding="utf-8")
    for script in SKILLS.glob("scraper-*/scripts/*.py"):
        remove_example_fallbacks(script)
    for doc in SKILLS.glob("*/SKILL*.md"):
        modernize_doc(doc)
    for doc in SKILLS.glob("*/SKILL.md"):
        slim_long_skill(doc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
