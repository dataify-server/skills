# Contributing to Dataify Skills

Thanks for your interest in contributing! This guide will help you add new skills or improve existing ones.

## Skill Structure

Every skill lives flat under the `skills/` directory and follows this layout:

```
skills/
├── dataify-web-unlocker/                 # Web Unlocker (1 skill)
├── serp-<engine>-<vertical>/             # SERP skills (25 skills)
├── scraper-<platform>-<resource>-by-<method>/   # Scraper skills (37 skills)
└── ...
```

Each individual skill directory contains:

```
skill-name/
├── SKILL.md              # Skill documentation (required)
├── SKILL.zh-CN.md        # Chinese documentation (required)
├── agents/
│   └── openai.yaml       # OpenAI/Codex agent config (required)
├── scripts/
│   └── main_script.py    # Execution script (required)
├── references/           # API reference docs (optional)
│   └── <name>_api.md
└── assets/               # Skill icons (optional)
    ├── <skill>-small.svg
    └── <skill>-large.svg
```

## Skill Categories

There is no nested category directory. Skills are identified by their directory prefix:

| Prefix | Category | Count | Example |
|--------|----------|-------|---------|
| `dataify-web-unlocker` | Web Unlocker | 1 | `dataify-web-unlocker` |
| `serp-*` | Search engine results | 25 | `serp-google-search`, `serp-bing-images` |
| `scraper-*` | Structured data extraction | 37 | `scraper-amazon-product`, `scraper-youtube-video-by-url` |

## Naming Convention

- **Directory name** uses the pattern `<prefix>-<engine|platform>-<resource>-by-<method>` where applicable. Examples:
  - `serp-google-search`
  - `serp-bing-images`
  - `scraper-amazon-product`
  - `scraper-youtube-video-by-url`
- **Frontmatter `name`** in `SKILL.md` uses the `dataify-` prefix, matching the skill's slash-command identifier. Examples: `dataify-google-search`, `dataify-amazon-product`.

## Adding a New Skill

### 1. Write SKILL.md

The `SKILL.md` is the most important file. It must include YAML frontmatter with `name` and `description`:

```markdown
---
name: dataify-<your-skill-name>
description: Brief description of what this skill does and when to trigger it.
---

# Skill Title

One-paragraph summary of the skill.

## API TOKEN Handling

(Standard token resolution section — copy from an existing skill)

## Core Workflow

1. Step-by-step workflow the agent should follow
2. Parameter validation and confirmation
3. API call execution
4. Result handling

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| param1    | string | Yes    | Description |

## Output

Describe the expected output format.

## Error Handling

Describe common errors and how to handle them.
```

Also create a Chinese translation as `SKILL.zh-CN.md` alongside it.

### 2. Create agents/openai.yaml

The `openai.yaml` uses a simple `interface` block (not a tool schema):

```yaml
interface:
  display_name: "Dataify <Skill Name>"
  short_description: "One-line description"
  default_prompt: "Use $dataify-<skill-name> to <what the agent should do>."

policy:
  allow_implicit_invocation: true   # optional — used by scraper skills
```

- `display_name` — human-readable name shown in the UI.
- `short_description` — one-line summary.
- `default_prompt` — the prompt used when the agent invokes the skill by its `$dataify-<name>` identifier.
- `policy.allow_implicit_invocation` — optional; enable for skills that may be triggered without an explicit slash command.

### 3. Implement scripts/

Write the Python execution script. Conventions:

- SERP skills: `scripts/<engine>_<vertical>.py` (e.g. `google_search.py`, `bing_images.py`), plus `scripts/preview_params.py` for parameter preview tables.
- Scraper skills: `scripts/submit_<platform>_<resource>.py` (e.g. `submit_amazon_product.py`).
- Web Unlocker: `scripts/invoke-dataify-web-unlocker.py`.

Script requirements:

- Use `DATAIFY_API_TOKEN` from environment variables.
- Accept `--token` to override the environment token for one run.
- Handle HTTP errors gracefully and return structured JSON responses.
- Include clear error messages.
- Support a `--dry-run` flag to print the normalized payload without calling the API where applicable.

### 4. Add references/ (optional)

For SERP skills, add `references/<engine>_<vertical>_api.md` documenting the full field list and examples. Scraper skills use `references/api.md`.

### 5. Add assets/ (optional)

If the skill needs icons, add `assets/<skill>-small.svg` and `assets/<skill>-large.svg`.

### 6. Test Your Skill

Before submitting:

- [ ] `SKILL.md` has correct frontmatter (`name` with `dataify-` prefix, `description`)
- [ ] `SKILL.zh-CN.md` exists and matches the English content
- [ ] `agents/openai.yaml` has a valid `interface` block
- [ ] Python script runs without errors (`python3 -m py_compile`)
- [ ] API TOKEN handling follows the standard pattern
- [ ] Parameters are documented with types and required/optional flags
- [ ] Error cases are handled

## Improving Existing Skills

- **Fix bugs** — Submit a PR with a clear description of the issue and fix
- **Update Chinese docs** — Keep `SKILL.zh-CN.md` in sync with `SKILL.md`
- **Improve descriptions** — Make skill descriptions clearer and more specific

## Commit Convention

Use clear, descriptive commit messages:

```
feat: add dataify-twitter-followers skill
fix: correct parameter validation in amazon-product skill
docs: add Chinese documentation for youtube skills
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/add-new-skill`
3. Make your changes following the guidelines above
4. Test your skill end-to-end
5. Submit a PR with:
   - Summary of changes
   - Which skill(s) are affected
   - Testing steps

## Questions?

If you have questions, open an [issue](https://github.com/dataify-server/skills/issues) on GitHub.
