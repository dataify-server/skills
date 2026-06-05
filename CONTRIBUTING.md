# Contributing to Dataify Skills

Thanks for your interest in contributing! This guide will help you add new skills or improve existing ones.

## Skill Structure

Every skill must follow this standard layout:

```
skill-name/
├── SKILL.md              # Skill documentation (required)
├── SKILL.zh-CN.md        # Chinese documentation (optional)
├── agents/
│   └── openai.yaml       # OpenAI agent configuration (required)
├── scripts/
│   └── main_script.py    # Execution script (required)
└── references/
    └── api.md            # API reference (optional)
```

## Adding a New Skill

### 1. Choose the Right Category

Place your skill under the appropriate category directory:

| Category | Directory | Use Case |
|----------|-----------|----------|
| Builder | `dataify-builder-skills/` | Generic platform scrapers |
| SERP | `serp-skills/<engine>/` | Search engine results (Google, Bing, etc.) |
| Amazon | `amazon-skills/` | Amazon data collection |
| YouTube | `youtube-skills/` | YouTube data collection |
| Facebook | `facebook-skills/` | Facebook data collection |
| Instagram | `instagram-skills/` | Instagram data collection |
| Google | `google-skills/` | Google Maps & Shopping |
| Reddit | `reddit-skills/` | Reddit data collection |
| Indeed | `indeed-skills/` | Indeed job data |
| eBay | `ebay-skills/` | eBay product data |
| Walmart | `walmart-skills/` | Walmart product data |
| Booking | `booking-skills/` | Booking.com hotel data |
| Web Unlocker | `dataify-web-unlocker/` | Web page unlocking |

For a new platform, create a new `<platform>-skills/` directory.

### 2. Naming Convention

Skill directories follow the pattern:

```
dataify-<platform>-<resource>-by-<method>
```

Examples:
- `dataify-amazon-product-by-asin`
- `dataify-google-search`
- `dataify-youtube-comment-by-id`

### 3. Write SKILL.md

The `SKILL.md` is the most important file. It must include:

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
| param2    | number | No     | Description |

## Output

Describe the expected output format.

## Error Handling

Describe common errors and how to handle them.
```

### 4. Create agents/openai.yaml

Define the OpenAI agent configuration with tool schemas:

```yaml
name: dataify-<your-skill-name>
description: >
  Brief description matching SKILL.md
instructions: >
  Detailed agent instructions
tools:
  - type: function
    function:
      name: submit_task
      description: Submit a data collection task
      parameters:
        type: object
        properties:
          param1:
            type: string
            description: Description
        required:
          - param1
```

### 5. Implement scripts/

Write the Python execution script. Follow these conventions:

- Use `DATAIFY_API_TOKEN` from environment variables
- Handle HTTP errors gracefully
- Return structured JSON responses
- Include clear error messages

### 6. Test Your Skill

Before submitting:

- [ ] `SKILL.md` has correct frontmatter (`name`, `description`)
- [ ] `agents/openai.yaml` has valid tool definitions with JSON schema
- [ ] Python script runs without errors
- [ ] API TOKEN handling follows the standard pattern
- [ ] Parameters are documented with types and required/optional flags
- [ ] Error cases are handled

## Improving Existing Skills

- **Fix bugs** — Submit a PR with a clear description of the issue and fix
- **Add Chinese docs** — Create `SKILL.zh-CN.md` alongside the existing `SKILL.md`
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
