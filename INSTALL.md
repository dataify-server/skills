---
name: dataify-setup
description: Check, install, authenticate, and use Dataify Skills, including ai-web-search, ai-web-extract, and ai-web-map.
user-invocable: true
metadata:
  author: dataify
---

# Dataify Skills Setup

If you are an agent running this file, first check whether the Dataify Skills are installed. If they are missing, download them before giving usage instructions.

## Step 1: Check

Default skill root: `${DATAIFY_SKILLS_DIR:-$HOME/.dataify/skills}`.

```bash
export DATAIFY_SKILLS_DIR="${DATAIFY_SKILLS_DIR:-$HOME/.dataify/skills}"
for file in \
  "$DATAIFY_SKILLS_DIR/skills/ai-web-search/SKILL.md" \
  "$DATAIFY_SKILLS_DIR/skills/ai-web-extract/SKILL.md" \
  "$DATAIFY_SKILLS_DIR/skills/ai-web-map/SKILL.md"; do
  if [ -f "$file" ]; then echo "FOUND $file"; else echo "MISSING $file"; fi
done
```

Windows PowerShell:

```powershell
$SkillRoot = if ($env:DATAIFY_SKILLS_DIR) { $env:DATAIFY_SKILLS_DIR } else { Join-Path $HOME ".dataify\skills" }
$required = @(
  "$SkillRoot\skills\ai-web-search\SKILL.md",
  "$SkillRoot\skills\ai-web-extract\SKILL.md",
  "$SkillRoot\skills\ai-web-map\SKILL.md"
)
@($required | Where-Object { -not (Test-Path -LiteralPath $_) }) | ForEach-Object { "MISSING $_" }
```

## Step 2: Download if missing

macOS/Linux:

```bash
export DATAIFY_SKILLS_DIR="${DATAIFY_SKILLS_DIR:-$HOME/.dataify/skills}"
if [ -d "$DATAIFY_SKILLS_DIR/.git" ]; then
  git -C "$DATAIFY_SKILLS_DIR" pull --ff-only
else
  mkdir -p "$(dirname "$DATAIFY_SKILLS_DIR")"
  git clone https://github.com/dataify-server/skills.git "$DATAIFY_SKILLS_DIR"
fi
```

Windows PowerShell:

```powershell
$SkillRoot = if ($env:DATAIFY_SKILLS_DIR) { $env:DATAIFY_SKILLS_DIR } else { Join-Path $HOME ".dataify\skills" }
if (Test-Path "$SkillRoot\.git") {
  git -C $SkillRoot pull --ff-only
} else {
  New-Item -ItemType Directory -Force -Path (Split-Path $SkillRoot) | Out-Null
  git clone https://github.com/dataify-server/skills.git $SkillRoot
}
$env:DATAIFY_SKILLS_DIR = $SkillRoot
```

Requirements: Git and Python 3.11 or newer.

If your agent discovers skills from a global directory, register the folders `ai-web-search`, `ai-web-extract`, and `ai-web-map`, or point it at `$DATAIFY_SKILLS_DIR/skills`.

## Step 3: Sign in

Dataify Skills use an API token; there is no separate username/password login command.

1. Open https://dashboard.dataify.com/login?utm_source=skill
2. Sign in or create an account.
3. Copy an API token.
4. Set `DATAIFY_API_TOKEN` in the environment. Do not paste it into chat.

```bash
export DATAIFY_API_TOKEN="your_token_here"
export AI_WEB_API_BASE_URL="https://aiwebapi.dataify.com"
```

```powershell
$env:DATAIFY_API_TOKEN = "your_token_here"
$env:AI_WEB_API_BASE_URL = "https://aiwebapi.dataify.com"
```

The AI Web scripts default to `https://aiwebapi.dataify.com`; the variable is needed only to override the environment.

Verify without exposing the token:

```bash
if [ -n "$DATAIFY_API_TOKEN" ]; then echo "configured"; else echo "missing"; fi
```

## Step 4: Use ai-web-search

```bash
python3 "$DATAIFY_SKILLS_DIR/skills/ai-web-search/scripts/search.py" web --query "AI news" --time-range week --max-results 3
python3 "$DATAIFY_SKILLS_DIR/skills/ai-web-search/scripts/search.py" shopping --query "wireless mouse" --max-results 3
python3 "$DATAIFY_SKILLS_DIR/skills/ai-web-search/scripts/search.py" news --query "OpenAI" --time-range week --max-results 3
python3 "$DATAIFY_SKILLS_DIR/skills/ai-web-search/scripts/search.py" scholar --query "large language models" --language en --max-results 3
```

Fixed identities:

- web: `search_web` + `web`
- shopping: `search_shopping` + `shopping`
- news: `search_news` + `news`
- scholar: `search_scholar` + `scholar`

`time_range` is supported by web and news only. Shopping and scholar do not support it. Shopping also does not take an input `url`. Web country values must be uppercase, for example `US`.

Search with result extraction:

```bash
python3 "$DATAIFY_SKILLS_DIR/skills/ai-web-search/scripts/search.py" news \
  --query "OpenAI" --max-results 1 \
  --extract-content --extract-format markdown
```

## Step 5: Use ai-web-extract

```bash
python3 "$DATAIFY_SKILLS_DIR/skills/ai-web-extract/scripts/extract.py" \
  --url "https://example.com/article" --format markdown --format links
```

Common options: `--only-main-content`, `--include-tag`, `--exclude-tag`, `--header`, `--timeout-ms`, `--wait-for-ms`, `--max-age-ms`, `--country US`, `--advanced-mode`.

## Step 6: Use ai-web-map

```bash
python3 "$DATAIFY_SKILLS_DIR/skills/ai-web-map/scripts/map.py" \
  --url "https://www.dataify.com/" --limit 100
```

Common options: `--country US`, `--domain-filter domain|all`, `--limit`, `--sitemap skip|include|only`.


## Suggested first run

```bash
python3 "$DATAIFY_SKILLS_DIR/skills/ai-web-search/scripts/search.py" web \
  --query "AI news" --max-results 1 --dry-run
```

After authentication, run the same command without `--dry-run`. Never put the token in command-line arguments or package files.