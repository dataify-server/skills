# Dataify 公共产品与 Skills 转化完整优化方案

> 文档状态：评审稿  
> 基线日期：2026-08-31  
> 适用范围：Dataify 公共 GitHub、Skills、MCP、CLI、Plugin、SDK、ClawHub 分发与注册激活链路  
> 本文是对既有竞品方案的校正版：核心问题定义为“能力已较完整，但产品入口、公开契约和首次成功路径不统一”，不再把公开展示缺口等同于底层能力缺失。

## 1. 执行摘要

Dataify 已经具备较完整的 Web Data 产品栈：63+ Agent Skills、Hosted MCP、HTTP/SSE/stdio 接入、CLI、OpenClaw Plugin、Python/TypeScript/Go/Java SDK，以及 Web Unlocker、SERP、平台采集、异步任务、状态查询、结果下载、余额和用量查询等能力。

当前最值得解决的不是继续横向堆叠工具，而是把分散能力组织成一条低摩擦且可观测的用户路径：

```text
发现 Skill → 理解价值 → 安装 → 获取凭据 → 首次调用 → 等待任务 → 拿到结果 → 理解成本 → 复用/付费
```

核心目标：

- 统一产品入口和能力口径，消除仓库之间的认知冲突。
- 统一认证、域名、命令、状态和错误契约，确保示例可复制运行。
- 将异步任务的提交、等待、下载包装成默认闭环。
- 用 Router、CLI 和场景型 Skill 降低用户的选择成本。
- 建立从下载到注册、首次成功和持续使用的完整漏斗。

建议先执行 6 周 P0/P1 计划，不以新增数据源数量作为本阶段成功指标。

## 2. 能力定义

### 2.1 用户能力

目标用户安装任一 Dataify 入口后，应能在不了解底层 API 和任务状态机的情况下：

1. 根据业务目标选择正确工具。
2. 用一个统一凭据完成认证。
3. 在 5 分钟内完成首次有效调用。
4. 对同步任务直接获得结果，对异步任务自动等待并下载结果。
5. 清楚看到结果来源、耗时、积分成本和后续操作。
6. 在 Skills、MCP、CLI 和 SDK 之间迁移时保持一致心智模型。

### 2.2 商业能力

Dataify 应能识别并衡量：

- 哪个渠道带来安装和注册。
- 用户在哪一步流失。
- 哪个 Skill 带来首次成功和后续留存。
- 首次结果的耗时、成功率和积分成本。
- 免费额度是否带来有效激活，而非无价值消耗。

## 3. 当前公开能力基线

截至基线日期，`dataify-server` GitHub 公开账号包含 9 个仓库：

| 产品面 | 公开仓库 | 已有能力 | 本阶段判断 |
| --- | --- | --- | --- |
| 总览 | `dataify-server` | 产品矩阵、快速开始、Tool Groups | 保留并升级为单一导航入口 |
| Skills | `skills` | 63+ Skills、安装脚本、Agent onboarding | 能力充足，需入口收敛和契约统一 |
| MCP | `mcp` | Hosted HTTP/SSE、stdio、工具分组 | 已存在，不重复建设 |
| CLI | `cli` | Token 配置、工具发现、Schema、通用调用、Chat | 已存在，补齐产品化快捷命令 |
| Plugin | `plugin` | OpenClaw/ClawHub、远程 MCP 注册 | 已存在，强化首跑与归因 |
| Python SDK | `dataify-sdk-python` | SERP、45 个采集器、错误类型 | 已存在，统一命名和任务体验 |
| TypeScript SDK | `dataify-sdk-ts` | SERP、Web Unlocker、任务结果下载 | 已存在，补充统一等待接口 |
| Go SDK | `dataify-sdk-go` | 71 个 API Runtime Tools | 已存在，补齐公开契约说明 |
| Java SDK | `dataify-sdk-java` | 71 个 API Runtime Tools | 已存在，修复公开文档质量 |

结论：Dataify 与 Bright Data 的主要差距是产品编排、信任和激活效率，不是基础工具覆盖数量。

## 4. 当前问题与根因

### 4.1 能力口径不一致

公开页面同时出现 25+ MCP Tools、140+ MCP Tools、71 API Runtime Tools、63+ Skills、45 个采集器等数字，但没有解释各自所属层级。

优化后的标准口径：

```text
MCP tools       = MCP 服务暴露的细粒度工具总数
API tools       = API Key 可直接调用的 Runtime Tools
Agent skills    = 面向 Agent 的操作说明和场景封装
Scrapers        = 结构化平台采集流程
Tool groups     = 按平台或用途加载的 MCP 工具组
```

所有数字必须由可生成的 manifest 提供，README 不允许手工维护计数。

### 4.2 认证变量不一致

当前公开文档出现 `DATAIFY_API_TOKEN`、`DATAIFY_MCP_TOKEN`、`DATAIFY_TOKEN`、`DATAIFY_API_KEY`。

决策建议：

- 新文档、新 CLI 和新 SDK 示例统一使用 `DATAIFY_API_KEY`。
- 运行时兼容读取旧变量，优先级为：

```text
DATAIFY_API_KEY
DATAIFY_API_TOKEN
DATAIFY_TOKEN
DATAIFY_MCP_TOKEN
```

- 读取旧变量时只输出一次弃用提示，不输出凭据内容。
- 两个小版本后再评估是否移除旧变量支持。

### 4.3 域名和注册链接分散

公开材料存在 `dataify.com`、`www.dataify.com`、`dashboard.dataify.com`、`doc.dataify.com`、`docs.dataify.com`。

需要定义固定职责：

| 用途 | 标准入口 | 状态 |
| --- | --- | --- |
| 官网 | 待产品确认 | 开放问题 |
| 注册/控制台 | 待产品确认 | 开放问题 |
| 开发文档 | 待产品确认 | 开放问题 |
| MCP | `mcp.dataify.com` | 已明确 |
| Runtime API | `scraperapi.dataify.com`、`webunlocker.dataify.com` | 已公开 |

在域名决策完成前，不做全仓机械替换。

### 4.4 CLI 文档与产品总览可能不一致

总览仓库展示 `dataify search`、`dataify scrape`，CLI README 主要展示 `dataify google_search`、`dataify request_web_unlocker` 和 `dataify call`。

要求通过契约测试确认命令是否真实存在。目标 CLI 命令面：

```bash
dataify login
dataify doctor
dataify search "latest AI news"
dataify scrape https://example.com
dataify run amazon-product --asin B0...
dataify task status <task_id>
dataify task wait <task_id> --download --format json
dataify balance
dataify tools
dataify schema <tool>
dataify call <tool> [arguments]
```

快捷命令是稳定产品接口，`call` 是高级逃生口。

### 4.5 异步任务能力存在但闭环不统一

已有状态查询和结果下载能力，但用户仍可能需要理解任务 ID、轮询间隔、成功状态和下载接口。

默认体验应收敛为：

```text
提交 → 有界轮询 → 成功后下载 → 标准化输出
                    └→ 失败时返回可执行恢复建议
```

高级用户可以用 `--no-wait` 只获得任务句柄。

### 4.6 Skills 数量丰富但选择成本高

大量平台级 Skill 有利于长尾搜索，却不利于首次用户理解“应该安装哪个”。需要把产品入口分成三层：

1. 核心入口：onboarding、router、task operations。
2. 原子能力：Web Unlocker、SERP、平台采集器。
3. 结果型场景：竞品监控、价格监控、评论分析、Lead enrichment、SEO research。

原子 Skill 不删除；通过 Router 和场景 Skill 组织起来。

## 5. 目标产品架构

```text
Distribution
GitHub / ClawHub / npm / PyPI / Go / Maven
                    │
                    ▼
Entry & Onboarding
Profile README / Installer / Plugin / dataify login / doctor
                    │
                    ▼
Intent Routing
Router → scenario skill → atomic skill/tool
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
         MCP       CLI       SDK/REST
          └─────────┼─────────┘
                    ▼
Execution Orchestrator
sync result / async submit → wait → download / retry policy
                    │
                    ▼
Dataify Runtime
Web Unlocker / SERP / Scraper Builder
                    │
                    ▼
Growth & Operations
attribution / funnel / success rate / latency / credit cost
```

### 5.1 架构约束

- MCP、CLI、SDK 和 Skills 共用同一份工具 manifest。
- 状态映射、重试规则和错误分类只有一个事实源。
- SDK 不依赖 Agent Skill 才能正确运行。
- Skill 不复制完整 API Schema，只引用生成的工具描述或脚本帮助。
- 用户凭据不得写入 URL 日志、事件属性、错误上报或命令历史提示。
- 计费请求禁止默认无限重试。

## 6. 统一公开契约

### 6.1 工具 Manifest

建议新增机器可读文件：

```yaml
schema_version: 1
generated_at: 2026-08-31T00:00:00Z
products:
  skills: 63
  mcp_tools: 140
  api_runtime_tools: 71
  scraper_workflows: 45
  tool_groups: 23
tools:
  - id: google_search
    group: google_serp
    execution: sync
    billing: per_success
    surfaces: [mcp, cli, python, typescript, go, java]
```

README 中的数字、工具表和支持矩阵由此生成。

### 6.2 标准执行结果

CLI 和 Skill 脚本输出应能映射为：

```json
{
  "ok": true,
  "request_id": "req_xxx",
  "task_id": null,
  "status": "succeeded",
  "data": {},
  "meta": {
    "tool": "google_search",
    "duration_ms": 820,
    "credits_used": 1,
    "cached": false
  },
  "error": null
}
```

异步提交时 `status=queued` 且返回 `task_id`。不能改变上游响应时，由 CLI/SDK 适配层提供统一模型，并保留 `raw` 字段或 `--raw` 模式。

### 6.3 标准错误分类

| 错误类 | 是否重试 | 用户动作 |
| --- | --- | --- |
| `authentication_error` | 否 | 配置或更新 API Key |
| `permission_error` | 否 | 检查套餐和 Tool 权限 |
| `validation_error` | 否 | 修正参数 |
| `insufficient_credits` | 否 | 查看余额或充值 |
| `rate_limited` | 是 | 遵循 Retry-After |
| `transient_upstream` | 是 | 指数退避并限制次数 |
| `task_failed` | 条件性 | 根据失败原因决定是否重提 |
| `timeout` | 查询优先 | 先查状态，不直接重复提交 |

### 6.4 状态模型

对外统一：

```text
queued → running → succeeded
                 ├→ failed
                 ├→ cancelled
                 └→ expired
```

服务端中文或历史状态由适配层映射，不要求立即修改底层存储。

## 7. 异步任务编排方案

### 7.1 默认策略

- 首次轮询延迟 1 秒。
- 退避序列建议为 1、2、3、5、8、10 秒，之后维持 10 秒。
- 默认等待上限 120 秒；不同工具可以在 manifest 中覆盖。
- 遇到 HTTP 429 时尊重 `Retry-After`。
- 网络超时后优先按 task ID 查询，不自动重新提交计费任务。
- 成功后自动下载 JSON；大文件返回文件路径和摘要。
- 用户中断时输出 task ID 和恢复命令。

### 7.2 安全重试

- 只有具备幂等键或明确未被服务端接收时才自动重提。
- 每次提交生成 `idempotency_key`；服务端支持情况待确认。
- 默认最大提交次数为 1，状态查询允许安全重试。
- `task_failed` 必须根据错误原因分类，禁止无条件重跑。

### 7.3 CLI/SDK 接口

```text
submit(params) -> TaskHandle
get_status(task_id) -> TaskStatus
wait(task_id, timeout, poll_policy) -> CompletedTask
download(task_id, format) -> Result
run_and_wait(params, options) -> Result
```

`dataify-task-operations` 负责策略，`dataify-task-status` 和 `dataify-task-result` 负责原子调用。

## 8. Onboarding 与首次成功

### 8.1 统一入口选择

```text
AI Agent 用户       → Skills 或 MCP
终端/自动化用户     → CLI
应用开发者          → SDK/REST
OpenClaw 用户       → ClawHub Plugin
不确定的用户        → 交互式安装器
```

### 8.2 五分钟首跑

每个入口必须完成同一套验证：

1. 检测运行环境。
2. 检测 API Key；缺失时给出带来源参数的注册入口。
3. 执行 `doctor`，验证网络、认证和工具发现。
4. 推荐一个低成本同步示例。
5. 输出结果、耗时和积分消耗。
6. 推荐一个与当前意图相关的下一步。

### 8.3 CTA 规则

注册 CTA 必须回答：

- 注册后得到什么。
- 是否有免费额度及有效期。
- 什么时候扣费。
- 链接将跳到哪里。

所有链接携带：

```text
utm_source
utm_medium
utm_campaign
utm_content
skill_id
skill_version
```

API Key 和用户输入不得进入 UTM 参数。

## 9. Router 与 Skill 信息架构

### 9.1 Router 决策顺序

```text
用户是否指定工具？
├─ 是 → 校验工具和参数后执行
└─ 否 → 判断目标
       ├─ 搜索结果 → SERP
       ├─ 任意网页正文/截图 → Web Unlocker
       ├─ 平台结构化数据 → 对应 Scraper
       ├─ 多源业务结论 → 场景型 Skill
       └─ 不确定 → 先做产品/工具发现，不猜 spider_id
```

### 9.2 Skill 最低质量契约

每个公开 Skill 必须包含：

- 一句话结果承诺。
- 适用和不适用场景。
- 必填参数及一个真实格式示例。
- 最小可运行命令。
- 同步/异步说明。
- 预期输出示例。
- 计费和重试提示。
- 常见错误与恢复动作。
- 注册、文档和支持入口。
- 版本与兼容性信息。

### 9.3 首批场景型 Skills

优先构建：

1. 竞品价格与商品变化监控。
2. 评论采集与主题/情感分析。
3. 公司与 Lead enrichment。
4. SEO/SERP 竞争情报。
5. 社媒账号和内容表现研究。

场景型 Skill 编排现有原子能力，不重复开发采集接口。

## 10. GitHub、ClawHub 与包分发优化

### 10.1 GitHub

- 使用 `dataify-server/dataify-server` 承载 Profile README；确认 GitHub User Profile 展示规则后实施。
- Pin：总览、Skills、MCP、CLI、Plugin、一个主 SDK。
- 所有仓库补齐 description、topics、homepage、license 和 support。
- README 顶部统一导航和五分钟 Quick Start。
- 删除本机绝对路径等不应出现在公共文档中的内容，例如 Java README 的 Windows 参考路径。
- 为安装、Quick Start 和文档链接配置自动检查。

### 10.2 ClawHub

- 主推一个“Dataify MCP/Router”入口，平台原子 Skill 承担搜索流量。
- 商店首屏按“用户能获得的结果”描述，而不是罗列接口。
- 安装后第一条引导直接执行同步低成本示例。
- 在异步 Skill 中明确自动等待或恢复命令。
- 发布前执行 dry-run、来源 commit 校验和安装冒烟测试。

### 10.3 包管理器

- npm、PyPI、Go、Maven 的包名、版本、环境变量和官网入口保持一致。
- 发布流水线执行 README 示例测试。
- SDK 版本矩阵自动写入总览仓库。

## 11. 数据漏斗与可观测性

### 11.1 核心事件

| 事件 | 触发点 | 关键属性 |
| --- | --- | --- |
| `listing_viewed` | 分发页曝光 | channel、artifact_id |
| `install_started` | 开始安装 | client、os、artifact_id |
| `install_succeeded` | 安装完成 | duration、version |
| `signup_clicked` | 点击注册 | source、skill_id |
| `signup_completed` | 注册完成 | attribution_id |
| `credential_configured` | 凭据验证通过 | surface，不记录凭据 |
| `first_request_started` | 首次请求 | tool、execution_type |
| `first_request_succeeded` | 首次成功 | latency、credits_used |
| `task_completed` | 异步任务完成 | tool、wait_duration |
| `result_consumed` | 下载或输出结果 | format、result_size_bucket |
| `second_session` | 第二个活跃日/会话 | cohort |
| `paid_conversion` | 首次付费 | attribution_id |

### 11.2 指标定义

```text
安装转化率       = install_succeeded / listing_viewed
注册转化率       = signup_completed / install_succeeded
凭据激活率       = credential_configured / signup_completed
首次成功率       = first_request_succeeded / credential_configured
端到端激活率     = first_request_succeeded / install_succeeded
结果消费率       = result_consumed / task_completed
7 日留存         = 第 7 日活跃用户 / 激活用户
付费转化率       = paid_conversion / 激活用户
```

必须同时看转化率和样本量；每个指标按渠道、入口、Skill、版本、客户端和国家/地区分层。

### 11.3 隐私约束

- 不采集 API Key、Authorization Header、完整 URL 查询参数和用户原始搜索内容。
- 用户输入仅记录类别或不可逆摘要，且需经过隐私评审。
- CLI 遥测必须公开说明并支持关闭。
- 服务端请求日志和产品分析事件使用不同数据权限。

## 12. 质量保障与 CI 门禁

### 12.1 自动检查

- Skill frontmatter、目录名和脚本入口一致。
- README 中命令可解析，核心命令执行冒烟测试。
- 所有公开链接返回有效状态。
- 环境变量只使用标准名称，兼容变量只允许出现在迁移章节。
- Manifest 计数与生成文档一致。
- 不允许密钥、真实 Token、本机绝对路径和 `__pycache__` 进入发布包。
- 异步任务状态映射具备单元测试和契约测试。

### 12.2 E2E 场景

至少覆盖：

1. 新用户安装 → 注册 → 配置 Key → Google Search 成功。
2. Amazon 异步提交 → 自动等待 → JSON 下载。
3. 任务等待中断 → 使用 task ID 恢复。
4. Key 无效 → 清晰认证错误和恢复动作。
5. 余额不足 → 无自动重试，展示余额入口。
6. 429/临时错误 → 有界退避且不重复计费提交。
7. MCP、CLI、Python 和 TypeScript 对同一工具的关键字段一致。

## 13. 实施路线图

### Phase 0：事实基线与契约冻结，3–5 天

- 确认标准域名、API Key 名称和产品数字定义。
- 生成公开仓库与包版本清单。
- 核验所有 README Quick Start。
- 建立当前下载、注册、首次调用和成功率基线。

交付物：能力 manifest v1、公开契约决策记录、漏斗基线。

### Phase 1：公开面一致性，1 周

- 统一 README 导航、数字、域名和凭据文案。
- 修复 CLI 总览与实际命令差异。
- 清理公共文档中的本机路径和过期链接。
- 增加链接、密钥和示例检查。

交付物：统一公开入口和 CI 文档门禁。

### Phase 2：首次成功闭环，1–2 周

- 实现 `dataify doctor`。
- 实现 CLI 快捷命令和认证引导。
- 为主要 Skill 增加可复制首跑。
- 建立安装、注册、凭据、首次请求事件链。

交付物：五分钟首跑和基础转化看板。

### Phase 3：异步任务统一，1–2 周

- 统一状态模型和错误分类。
- 实现 `task wait`、`run_and_wait` 和中断恢复。
- 接入 TypeScript/Python，再按使用量扩展 Go/Java。
- 完成重复计费和超时场景测试。

交付物：跨入口异步任务闭环。

### Phase 4：Router 与场景增长，2–4 周

- 升级 Router 选择逻辑。
- 发布首批 3–5 个场景型 Skills。
- 优化 ClawHub 主入口与原子 Skill 互链。
- 基于漏斗进行 CTA、首跑示例和免费权益实验。

交付物：结果型产品入口和持续实验机制。

## 14. 优先级与投入估算

| 优先级 | 工作项 | 主要角色 | 估算 |
| --- | --- | --- | --- |
| P0 | 公开契约和 README 一致性 | 产品 + DevRel + 工程 | 3–5 人日 |
| P0 | Quick Start 自动验证 | 工程 + QA | 3–5 人日 |
| P0 | 漏斗事件和基线 | 后端 + 数据 | 5–8 人日 |
| P0 | task wait/run_and_wait | CLI/SDK + 后端 | 8–12 人日 |
| P1 | doctor/login/快捷命令 | CLI 工程 | 5–8 人日 |
| P1 | Router 升级 | Agent/Skill 工程 | 5–8 人日 |
| P1 | GitHub/ClawHub 入口升级 | DevRel + 增长 | 3–5 人日 |
| P2 | 3–5 个场景型 Skills | 产品 + Agent 工程 | 8–15 人日 |

估算不包含底层 API 改造；若缺少幂等键、统一状态或事件归因能力，需要单独评估。

## 15. 验收标准

### 15.1 产品验收

- 新用户能在 5 分钟内从任一主入口获得首次结果。
- 所有主入口使用同一认证名、域名和能力解释。
- 用户不需要手工拼接状态与下载接口即可获得异步结果。
- 任一失败路径都返回明确原因、是否重试和下一步动作。

### 15.2 工程验收

- README 核心示例在 CI 中通过。
- 工具计数和支持矩阵全部由 manifest 生成。
- CLI/SDK/Skill 对外状态映射一致。
- 异步任务中断后可恢复，不重复提交计费任务。
- 发布包不包含凭据、本机路径、缓存文件。

### 15.3 业务目标

由于当前缺少完整漏斗基线，以下采用相对目标：

- 安装到注册转化率提升至少 50%。
- 注册到首次成功率提升至少 30%。
- 首次成功中位耗时降低至少 40%。
- 异步任务成功但未消费结果的比例降低至少 50%。
- 7 日留存提升至少 20%。

实验至少运行一个完整使用周期，并设置最小样本量后再判断结果。

## 16. 非目标

- 不在本阶段为了对标竞品盲目新增大量数据源。
- 不重写现有 MCP、CLI 或全部 SDK。
- 不强制删除平台原子 Skills。
- 不承诺底层接口尚未验证的 OAuth、幂等键或 Webhook 能力。
- 不用下载量单一指标判断产品成功。
- 不在未经验证时宣称所有 140+ 工具在所有 SDK 中完全等价。

## 17. 风险与护栏

| 风险 | 护栏 |
| --- | --- |
| 文档统一后仍与运行时不一致 | README 示例进入 CI，版本发布绑定测试结果 |
| 自动重试造成重复计费 | 只重试安全操作；提交默认不自动重试 |
| Router 误选高成本工具 | 优先同步低成本工具，执行前提示显著成本 |
| 遥测引发隐私问题 | 默认最小化采集、脱敏、可关闭、独立权限 |
| 多仓同时改造产生漂移 | Manifest 和模板集中维护，自动生成下游文档 |
| 旧环境变量立即失效 | 保留兼容层和弃用周期 |

## 18. 开放问题

以下问题在进入对应实现前必须确认：

1. 官网、Dashboard 和开发文档的标准域名分别是什么？
2. 标准凭据名称最终采用 `API_KEY` 还是 `API_TOKEN`？
3. 服务端是否支持幂等键和按 task ID 的强一致状态查询？
4. 各类异步任务的平均、P95 和最长完成时间是多少？
5. 失败任务是否计费，不同失败原因能否机器识别？
6. ClawHub 是否能提供曝光、安装和卸载事件，还是需要代理指标？
7. 免费额度、有效期和成功请求计费规则的最终公开文案是什么？
8. CLI 是否已经发布到 npm，公开包名和命令与总览是否一致？
9. 哪个 SDK 是优先维护的参考实现？
10. 是否计划将 GitHub User 迁移为 Organization？

## 19. 实施交接

当前方案可进入产品与架构联合评审，但还不能一次性直接实施全部内容。

建议交接顺序：

1. 产品负责人决策域名、凭据名、免费权益和产品数字口径。
2. 工程负责人核验 CLI 命令、任务状态、幂等和计费约束。
3. 数据负责人建立现状漏斗和事件字典。
4. DevRel 统一 GitHub、ClawHub 和包管理器公开面。
5. CLI/SDK 团队实现任务闭环和首次成功路径。
6. 完成 P0/P1 后，再用真实数据决定场景型 Skill 的优先级。

### 评审决策门

满足以下条件后进入开发：

- 标准域名与凭据名称已确认。
- 当前公开命令已完成真实性核验。
- 异步任务状态、计费和安全重试边界已确认。
- 漏斗事件具有明确数据归属和隐私审查结论。
- P0/P1 工作有明确仓库 Owner 和发布日期。

