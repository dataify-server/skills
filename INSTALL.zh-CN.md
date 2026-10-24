---
name: dataify-setup
description: 检查、安装、登录并说明如何使用 Dataify Skills，包括 ai-web-search、ai-web-extract 和 ai-web-map。
user-invocable: true
metadata:
  author: dataify
---

# Dataify Skills 安装与使用说明

如果你是正在执行本文件的 Agent，请先检查 Dataify Skills 是否已安装。缺失时直接下载安装，再向用户说明登录和使用方法。

## 第一步：检查

默认根目录：`${DATAIFY_SKILLS_DIR:-$HOME/.dataify/skills}`。

```bash
export DATAIFY_SKILLS_DIR="${DATAIFY_SKILLS_DIR:-$HOME/.dataify/skills}"
for file in \
  "$DATAIFY_SKILLS_DIR/skills/ai-web-search/SKILL.md" \
  "$DATAIFY_SKILLS_DIR/skills/ai-web-extract/SKILL.md" \
  "$DATAIFY_SKILLS_DIR/skills/ai-web-map/SKILL.md"; do
  if [ -f "$file" ]; then echo "FOUND $file"; else echo "MISSING $file"; fi
done
```

Windows PowerShell：

```powershell
$SkillRoot = if ($env:DATAIFY_SKILLS_DIR) { $env:DATAIFY_SKILLS_DIR } else { Join-Path $HOME ".dataify\skills" }
$required = @(
  "$SkillRoot\skills\ai-web-search\SKILL.md",
  "$SkillRoot\skills\ai-web-extract\SKILL.md",
  "$SkillRoot\skills\ai-web-map\SKILL.md"
)
@($required | Where-Object { -not (Test-Path -LiteralPath $_) }) | ForEach-Object { "MISSING $_" }
```

## 第二步：缺失时下载

macOS/Linux：

```bash
export DATAIFY_SKILLS_DIR="${DATAIFY_SKILLS_DIR:-$HOME/.dataify/skills}"
if [ -d "$DATAIFY_SKILLS_DIR/.git" ]; then
  git -C "$DATAIFY_SKILLS_DIR" pull --ff-only
else
  mkdir -p "$(dirname "$DATAIFY_SKILLS_DIR")"
  git clone https://github.com/dataify-server/skills.git "$DATAIFY_SKILLS_DIR"
fi
```

Windows PowerShell：

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

要求：Git 和 Python 3.11 或更高版本。

如果 Agent 通过全局 skills 目录发现 Skill，请注册 `ai-web-search`、`ai-web-extract`、`ai-web-map` 三个目录，或让 Agent 使用 `$DATAIFY_SKILLS_DIR/skills`。

## 第三步：登录

Dataify Skills 使用 API Token，不需要单独的用户名/密码登录命令。

1. 打开 https://dashboard.dataify.com/login?utm_source=skill
2. 登录或注册账号。
3. 复制 API Token。
4. 设置 `DATAIFY_API_TOKEN`，不要粘贴到聊天中。

```bash
export DATAIFY_API_TOKEN="your_token_here"
export AI_WEB_API_BASE_URL="https://aiwebapi.dataify.com"
```

```powershell
$env:DATAIFY_API_TOKEN = "your_token_here"
$env:AI_WEB_API_BASE_URL = "https://aiwebapi.dataify.com"
```

AI Web 脚本默认使用 `https://aiwebapi.dataify.com`，该变量只用于切换环境。

检查 Token，但不要打印 Token：

```bash
if [ -n "$DATAIFY_API_TOKEN" ]; then echo "configured"; else echo "missing"; fi
```

## 第四步：使用 ai-web-search

```bash
python3 "$DATAIFY_SKILLS_DIR/skills/ai-web-search/scripts/search.py" web --query "AI 最新资讯" --time-range week --max-results 3
python3 "$DATAIFY_SKILLS_DIR/skills/ai-web-search/scripts/search.py" shopping --query "笔记本电脑优惠" --max-results 3
python3 "$DATAIFY_SKILLS_DIR/skills/ai-web-search/scripts/search.py" news --query "OpenAI" --time-range week --max-results 3
python3 "$DATAIFY_SKILLS_DIR/skills/ai-web-search/scripts/search.py" scholar --query "大语言模型" --language en --max-results 3
```

固定身份：

- 网页搜索：`search_web` + `web`
- 购物搜索：`search_shopping` + `shopping`
- 新闻搜索：`search_news` + `news`
- 学术搜索：`search_scholar` + `scholar`

`time_range` 只支持网页搜索和新闻搜索。购物搜索不支持 `time_range`，也不接收输入 `url`。网页搜索的国家码必须大写，例如 `US`。

搜索并提取正文：

```bash
python3 "$DATAIFY_SKILLS_DIR/skills/ai-web-search/scripts/search.py" news \
  --query "OpenAI" --max-results 1 \
  --extract-content --extract-format markdown
```

## 第五步：使用 ai-web-extract

```bash
python3 "$DATAIFY_SKILLS_DIR/skills/ai-web-extract/scripts/extract.py" \
  --url "https://example.com/article" --format markdown --format links
```

常用参数：`--only-main-content`、`--include-tag`、`--exclude-tag`、`--header`、`--timeout-ms`、`--wait-for-ms`、`--max-age-ms`、`--country US`、`--advanced-mode`。

## 第六步：使用 ai-web-map

```bash
python3 "$DATAIFY_SKILLS_DIR/skills/ai-web-map/scripts/map.py" \
  --url "https://www.dataify.com/" --limit 100
```

常用参数：`--country US`、`--domain-filter domain|all`、`--limit`、`--sitemap skip|include|only`。

请使用 `--sitemap include` 或 `--sitemap skip`。正式环境测试发现 `--sitemap only` 会间歇性返回 HTTP 500。

## 建议首次运行

```bash
python3 "$DATAIFY_SKILLS_DIR/skills/ai-web-search/scripts/search.py" web \
  --query "AI news" --max-results 1 --dry-run
```

确认 Token 配置后，去掉 `--dry-run` 执行真实请求。不要把 Token 放进命令行参数或安装包。