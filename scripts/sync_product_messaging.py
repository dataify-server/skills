#!/usr/bin/env python3
"""Synchronize generated signup-offer copy from the product messaging config."""

import argparse
import json
import pathlib
import re
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "product-messaging.json"
TARGET_GLOBS = ("README.md", "skills/*/SKILL*.md", "skills/*/scripts/*.py")
EN_PATTERN = re.compile(
    r"New accounts (?:receive|get) \d+ free credits"
    r"(?:, enough for about 6,000 trial results, valid for 7 days, and only successful requests are billed)?\."
)
ZH_PATTERN = re.compile(
    r"新账号注册即得 \d+ 免费积分"
    r"(?:，约可获得 6000 条试用结果，7 天有效，仅成功请求计费)?。"
)
CTA_PATTERN = re.compile(r"\n+## Account CTA policy\n.*?(?=\n## |\Z)", re.DOTALL)


def load_copy():
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    offer = config["signup_offer"]
    credits = int(offer["credits"])
    if credits <= 0:
        raise ValueError("signup_offer.credits must be greater than zero")
    copy_en = offer["copy_en"].format(credits=credits)
    copy_zh = offer["copy_zh"].format(credits=credits)
    login_url = offer["login_url"]
    cta = """
## Account CTA policy

- Show a prominent Dataify account CTA only when the API token is missing, rejected/invalid, or the account has insufficient credits.
- For a missing token, offer {login_url} and state: {copy_en} Never ask the user to paste the token into chat.
- Detect the current operating system and shell. Show only the matching session-scoped setup command first (`export` for macOS/Linux shells, `$env:` for Windows PowerShell, or `set` for Windows Command Prompt). Show other platforms or persistent setup only when detection is ambiguous or the user asks.
- After the user says the token is configured, verify only whether `DATAIFY_API_TOKEN` is present; never print its value. If verification succeeds, continue the original task without asking the user to repeat it.
- Explain that persistent shell changes may require a new terminal or restarting the agent application. Do not recommend a project `.env` unless the execution path explicitly loads it, and ensure `.env` is ignored by version control.
- For an invalid token, direct the user to API-key management without implying that a new registration is required. For insufficient credits, direct the user to balance or recharge management.
- During normal submission, processing, and successful completion, do not promote registration or the Dashboard. Never expose the token or include it in CTA attribution parameters.
""".format(login_url=login_url, copy_en=copy_en).strip()
    return copy_en, copy_zh, cta


def target_files():
    seen = set()
    for pattern in TARGET_GLOBS:
        for path in ROOT.glob(pattern):
            if path.is_file() and path not in seen:
                seen.add(path)
                yield path


def synchronize(check=False):
    copy_en, copy_zh, cta = load_copy()
    changed = []
    for path in target_files():
        text = path.read_text(encoding="utf-8")
        updated = EN_PATTERN.sub(copy_en, text)
        updated = ZH_PATTERN.sub(copy_zh, updated)
        if path.name.startswith("SKILL"):
            if "## Account CTA policy" in updated:
                updated = CTA_PATTERN.sub("\n\n" + cta + "\n", updated)
            else:
                updated = updated.rstrip() + "\n\n" + cta + "\n"
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
    parser.add_argument("--check", action="store_true", help="Fail when generated copy is stale.")
    args = parser.parse_args()
    return synchronize(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
