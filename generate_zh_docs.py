#!/usr/bin/env python3
"""Batch generate SKILL.zh-CN.md for skills that don't have one yet."""

import os
import re

BASE = "/Users/gujingwen/dataify_skills"

# ── Translation mappings ──

SECTION_TRANSLATIONS = {
    "API TOKEN Handling": "API TOKEN 处理",
    "Core Workflow": "核心工作流程",
    "Parameter Checklists": "参数清单",
    "Mode Selection": "模式选择",
    "Script Usage": "脚本用法",
    "Required Pre-Call Confirmation": "调用前确认（必须）",
    "Workflow": "工作流程",
    "Field Mapping": "字段映射",
    "Output": "输出",
    "Error Handling": "错误处理",
}

PHRASE_TRANSLATIONS = [
    ("Submit ", "提交 "),
    ("collection jobs through Dataify Builder", "采集任务到 Dataify Builder"),
    ("After a successful submission, give the user the", "提交成功后，向用户提供"),
    ("and tell them to visit", "并告诉用户前往"),
    ("to view results", "查看结果"),
    ("to view or manage results", "查看或管理结果"),
    ("Use for Dataify", "用于 Dataify"),
    ("Builder tasks", "Builder 任务"),
    ("Use when the user", "当用户"),
    ("Trigger when the user asks for", "当用户要求"),
    ("Do not download result files", "不要下载结果文件"),
    ("Use `DATAIFY_API_TOKEN` as the long-term saved token name.", "使用 `DATAIFY_API_TOKEN` 作为长期保存的 token 名称。"),
    ("If the user provides a token in the request, use it for this run.", "如果用户在请求中提供了 token，则使用该 token。"),
    ("If no token is provided, first check whether `DATAIFY_API_TOKEN` is already saved locally in the environment.", "如果未提供 token，先检查环境变量中是否已保存 `DATAIFY_API_TOKEN`。"),
    ("If `DATAIFY_API_TOKEN` is saved locally, use it.", "如果本地已保存 `DATAIFY_API_TOKEN`，则直接使用。"),
    ("Do not call the Builder endpoint without a token.", "没有 token 不要调用 Builder 接口。"),
    ("Required", "必填"),
    ("No default", "无默认值"),
    ("Yes", "是"),
    ("No", "否"),
    ("Field", "字段"),
    ("Default", "默认值"),
    ("Notes", "说明"),
    ("Mode", "模式"),
    ("Use for", "用途"),
    ("Collector ID", "采集器 ID"),
]

TOKEN_SECTION_ZH = """## 设置 DATAIFY_API_TOKEN

推荐使用永久环境变量，而不是只在当前终端临时设置。

Windows PowerShell，当前用户永久设置：

```powershell
[Environment]::SetEnvironmentVariable("DATAIFY_API_TOKEN", "your_token_here", "User")
```

然后重新打开 PowerShell。如果当前会话也要立即生效，再执行：

```powershell
$env:DATAIFY_API_TOKEN = "your_token_here"
```

macOS 或 Linux，bash 永久设置：

```bash
echo 'export DATAIFY_API_TOKEN="your_token_here"' >> ~/.bashrc
source ~/.bashrc
```

macOS 或 Linux，zsh 永久设置：

```bash
echo 'export DATAIFY_API_TOKEN="your_token_here"' >> ~/.zshrc
source ~/.zshrc
```
"""


def generate_serp_zh(skill_dir, name, skill_md_content):
    """Generate zh-CN doc for SERP-type skills."""
    # Extract frontmatter
    fm = re.search(r"^---\s*\n(.*?)\n---", skill_md_content, re.DOTALL)
    desc = ""
    if fm:
        dm = re.search(r"description:\s*(.+)", fm.group(1))
        if dm:
            desc = dm.group(1).strip()

    # Extract title
    title_match = re.search(r"^#\s+(.+)$", skill_md_content, re.MULTILINE)
    title = title_match.group(1) if title_match else name

    # Determine engine and script from directory
    parts = skill_dir.split("/")
    # Find script name
    scripts_dir = os.path.join(BASE, skill_dir, "scripts")
    script_name = None
    if os.path.isdir(scripts_dir):
        for f in os.listdir(scripts_dir):
            if f.endswith(".py") and f != "preview_params.py":
                script_name = f
                break

    has_preview = os.path.exists(os.path.join(scripts_dir, "preview_params.py")) if os.path.isdir(scripts_dir) else False
    has_refs = os.path.isdir(os.path.join(BASE, skill_dir, "references"))

    content = f"""# {title} 中文版

这个 skill 用于将用户的搜索请求转化为 Dataify Scraper API 调用，并返回结构化搜索结果。

## 调用前确认（必须）

每次真正调用 API 之前，必须遵循以下确认流程：

1. 将用户请求解析为 API 参数字段和固定的 `engine` 值。
2. 仅在参数描述明确标注默认值时才使用默认值。不要将示例值、占位符或样例数据作为默认值。
3. 如果必填参数没有默认值且无法从用户请求中推断，先询问用户。
4. 调用 API 前展示 Markdown 参数表。不要包含 `Authorization`。表格必须包含以下列：`参数名`、`当前值`、`默认值`、`说明`。
5. 展示表格后询问用户是否需要修改参数。用户确认后才能调用 API。
6. 如果用户修改了参数，重新生成表格并再次确认。
7. 如果 token 缺失，提示用户前往 [Dataify Dashboard](https://dashboard.dataify.com?utm_source=skill) 获取 `DATAIFY_API_TOKEN`。
"""

    if has_preview:
        content += f"""
使用预览工具生成确认表格：

```bash
python3 scripts/preview_params.py --params-json '{{"q":"用户查询内容"}}'
```
"""

    content += f"""
## 工作流程

1. 解析用户请求，提取搜索参数。
2. 如果 token 缺失，提示用户前往 [Dataify Dashboard](https://dashboard.dataify.com?utm_source=skill) 获取 `DATAIFY_API_TOKEN`。
3. 构建请求参数，仅包含用户请求的字段和必要的默认值。
4. 使用 `python3` 运行脚本。

```bash
python3 scripts/{script_name} --params-json '{{"q":"搜索关键词"}}'
```

如果用户在对话中提供了 token，使用 `--token` 传递：

```bash
python3 scripts/{script_name} --token "USER_TOKEN" --params-json '{{"q":"搜索关键词"}}'
```

5. 将脚本输出直接返回给用户。不要对 API 响应进行总结、提取、清理、翻译或重新格式化。

{TOKEN_SECTION_ZH}
"""

    if has_refs:
        content += """## 参考文件

- `references/` 目录下的 API 文档包含完整的字段列表和说明。
- 当字段行为、允许的值或响应格式不明确时，请查阅参考文档。
"""

    content += f"""## 注意事项

- 始终使用 `Content-Type: application/x-www-form-urlencoded` 提交 API 请求。
- 保持请求值为字符串类型。
- 省略用户未请求的可选字段。
- 除非用户另有要求，否则不要对返回结果进行任何加工处理。
"""
    return content


def generate_builder_zh(skill_dir, name, skill_md_content):
    """Generate zh-CN doc for Builder-type skills."""
    # Extract title
    title_match = re.search(r"^#\s+(.+)$", skill_md_content, re.MULTILINE)
    title = title_match.group(1) if title_match else name

    # Extract first paragraph after title
    intro = ""
    intro_match = re.search(r"^#\s+.+\n\n(.+?)(?:\n\n|\n##)", skill_md_content, re.DOTALL)
    if intro_match:
        intro = intro_match.group(1).strip()

    # Extract mode table if exists
    mode_table = ""
    table_match = re.search(r"(\|.+\|[\s\S]*?\n\n)", skill_md_content)
    if table_match:
        mode_table = table_match.group(1).strip()

    # Find script
    scripts_dir = os.path.join(BASE, skill_dir, "scripts")
    script_name = None
    script_type = "builder"
    if os.path.isdir(scripts_dir):
        for f in sorted(os.listdir(scripts_dir)):
            if f.endswith(".py"):
                script_name = f
                if "submit" in f:
                    script_type = "submit"
                break

    # Detect parameter sections
    param_sections = re.findall(r"###\s+(.+)\n\n(\|.+\|[\s\S]*?)(?=\n###|\n##|\Z)", skill_md_content)

    content = f"# {title} 中文版\n\n"

    # Translate intro
    if intro:
        intro_zh = intro
        for en, zh in PHRASE_TRANSLATIONS:
            intro_zh = intro_zh.replace(en, zh)
        content += f"{intro_zh}\n\n"

    # Mode table
    if mode_table and "Mode" in mode_table:
        content += f"## 采集模式\n\n{mode_table}\n\n"

    content += """## API TOKEN 处理

使用 `DATAIFY_API_TOKEN` 作为长期保存的 token 名称。

- 如果用户在请求中提供了 token，则使用该 token。
- 如果未提供 token，先检查环境变量中是否已保存 `DATAIFY_API_TOKEN`。
- 如果本地已保存 `DATAIFY_API_TOKEN`，则直接使用。
- 如果没有可用的 token，提示用户前往 [Dataify](https://dashboard.dataify.com?utm_source=skill) 获取 API TOKEN。
- 没有 token 不要调用 Builder 接口。

"""

    content += TOKEN_SECTION_ZH

    content += """## 核心工作流程

1. 从用户请求中识别采集模式。
2. 提交前，以 Markdown 表格展示必填参数、可选参数和默认值。
3. 询问用户是否需要修改参数。
4. 规范化并验证最终参数值。
5. 获取 Dataify token（用户提供或已保存的 `DATAIFY_API_TOKEN`）。
6. 如果没有 token，提示用户前往 [Dataify](https://dashboard.dataify.com?utm_source=skill) 获取。
7. 提交 Builder 请求创建任务。
8. 从响应中读取 `data.task_id`。
9. 提交成功后停止，告诉用户前往 [Dataify](https://dashboard.dataify.com?utm_source=skill) 查看或管理结果。

"""

    # Parameter sections
    if param_sections:
        content += "## 参数清单\n\n"
        for section_name, section_content in param_sections:
            content += f"### {section_name}\n\n{section_content.strip()}\n\n"

    # Script usage
    if script_name:
        content += f"""## 脚本用法

使用 Python 运行：

```bash
python3 scripts/{script_name} --help
```

"""

    content += """## 注意事项

- 提交成功后不要下载结果文件，告诉用户前往 [Dataify](https://dashboard.dataify.com?utm_source=skill) 查看。
- 始终以 Markdown 表格展示参数确认，不要使用纯文本或项目列表。
- 如果用户已经提供了部分参数，在表格中显示这些值，只询问是否修改剩余参数。
"""
    return content


def main():
    # Find all skills missing zh-CN
    missing = []
    for root, dirs, files in os.walk(BASE):
        if ".git" in root:
            continue
        if "SKILL.md" in files and "SKILL.zh-CN.md" not in files:
            rel = os.path.relpath(root, BASE)
            missing.append(rel)

    missing.sort()
    print(f"Found {len(missing)} skills missing SKILL.zh-CN.md\n")

    created = 0
    for skill_dir in missing:
        skill_md_path = os.path.join(BASE, skill_dir, "SKILL.md")
        zh_path = os.path.join(BASE, skill_dir, "SKILL.zh-CN.md")

        with open(skill_md_path, "r", encoding="utf-8") as f:
            content_en = f.read()

        # Extract name from frontmatter
        name_match = re.search(r"name:\s*(.+)", content_en)
        name = name_match.group(1).strip() if name_match else os.path.basename(skill_dir)

        # Determine type
        is_serp = "serp-skills" in skill_dir

        if is_serp:
            zh_content = generate_serp_zh(skill_dir, name, content_en)
        else:
            zh_content = generate_builder_zh(skill_dir, name, content_en)

        with open(zh_path, "w", encoding="utf-8") as f:
            f.write(zh_content)

        created += 1
        print(f"CREATED: {skill_dir}/SKILL.zh-CN.md")

    print(f"\nDone. Created {created} files.")


if __name__ == "__main__":
    main()
