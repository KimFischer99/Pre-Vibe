# pre-vibe v0.3 架构报告

## 1. 结论

本次修改将 pre-vibe 从“生成三份 Markdown 的文本工具”调整为 **Codex Plugin 形式的首轮 intake workflow**。

新的核心定位是：

> 在 Codex 新 session 的早期，把用户短小、模糊、混乱或高风险的初始需求，转化为有证据、有边界、可执行的项目上下文；在用户确认后，只注入面向 Codex 执行的紧凑 `FIRST_PROMPT.md`。

这与 PRD 中的初始想法保持一致：pre-vibe 不是普通 prompt optimizer，也不是 text2text 改写器，而是面向 agent workflow 的上下文闸门。它会先澄清、扫描、检索和整理，再产出结果；缺少关键上下文时必须停下，不能假装完成。

## 2. 对照 PRD 的关键要求

| PRD / Workflow 要求 | v0.3 实现方式 |
|---|---|
| 以 Codex plugin 形式运行 | 保留 `.codex-plugin/plugin.json`，新增 `skills/pre-vibe/agents/openai.yaml` 和 `.mcp.json`。 |
| 深入融合 Codex，而不是反复显式调用 skill | 增加 Codex-facing agent manifest，允许隐式触发；插件描述和默认入口都面向自然 intake。 |
| 不只是生成三份模板 md | `scripts/pre_vibe.py` 不再生成 Markdown 正文，只提供状态机、扫描、环境检查、artifact 写入等工具能力。 |
| 需要自然交互 | `SKILL.md` 明确要求使用自然进度文案，不向用户反复暴露 plugin/skill 机制。 |
| 必须有询问和搜索/扫描环节 | 引入 `NEEDS_USER_INPUT` 和 `NEEDS_CONTEXT` 状态；未完成时禁止生成最终 `FIRST_PROMPT.md`。 |
| 三类任务 intake | workflow 支持 `general`、`research`、`coding`、`mixed`，并按场景选择不同上下文策略。 |
| 三档强度 | 用 `mini`、`default`、`architect` 替代旧 `micro/standard/deep/architect` 严格 token budget。 |
| 不再严格限定 token 消耗 | v0.3 不设硬 token 上限，但要求 `FIRST_PROMPT.md` 只保留最小可执行内容。 |
| 生成三份文档 | 保留 `PRE_VIBE_SPEC.md`、`INIT_AGENTS.md`、`FIRST_PROMPT.md`。 |
| SPEC 面向初级用户 | `SKILL.md` 和 `templates.md` 要求 SPEC 作为项目 handbook，用用户语言解释目标、边界、建议、风险和下一步。 |
| AGENTS/PROMPT 面向 agent | `INIT_AGENTS.md` 只放 durable guidance；`FIRST_PROMPT.md` 只放执行所需的目标、约束、文件指针和验收标准。 |
| 文档必须定制写作 | Artifact rules 明确禁止占位符、重复模板语言、泛泛建议和与插件内部组件相关的表述。 |
| 安全扫描 | `scan-policy.md` 和 `safe_walk()` 使用 allowlist，默认跳过 `.env`、token、私钥、数据库、生产日志等。 |
| INTAKE 不落盘 | `NEEDS_USER_INPUT` / `NEEDS_CONTEXT` 阶段的 intake notes 只保留在当前对话上下文，不写 `INTAKE.md`。 |
| 内置提问工具 | blocking questions 优先使用 Codex native question/user-input UI。 |
| 注入操作 | 用户批准后由 pre-vibe 执行 clear-context 并注入 `FIRST_PROMPT.md`，不再要求用户手动 `/clear`。 |
| AGENTS 不冲突 | `INIT_AGENTS.md` 必须参考全局 AGENTS.md，且不得加入冲突或削弱全局指令的规则。 |

## 3. 新架构

```text
User rough request
  -> Codex invokes pre-vibe workflow
  -> classify_intake
  -> state gate
      NEEDS_USER_INPUT: ask blocking questions
      NEEDS_CONTEXT: scan project / inspect Codex env / map sources
      READY_TO_COMPILE: write final artifacts
  -> user reviews AGENTS + FIRST_PROMPT
  -> user approves clear + injection
  -> pre-vibe clears context
  -> inject FIRST_PROMPT.md only
  -> pre-vibe exits
```

### 3.1 Plugin 层

`plugin.json` 描述 pre-vibe 为 Codex workflow plugin，并声明：

- `skills: ./skills/`
- `mcpServers: ./.mcp.json`
- `defaultPrompt` 为 3 条短入口提示
- version 为 `0.3.1+codex.20260606090140`

当前 Codex plugin 本地 validator 不接受 `hooks` 字段，所以 v0.3 没有伪造 session lifecycle hook。所谓“自动触发”通过以下方式接近实现：

- plugin 描述和 skill description 覆盖 vague/first-session request；
- `agents/openai.yaml` 开启 `allow_implicit_invocation`；
- MCP 工具让 Codex 可以自然调用状态机和扫描能力；
- skill 指令要求自然交互，不要求用户反复显式调用。

### 3.2 Skill Workflow 层

`SKILL.md` 现在是状态机协议，而不是线性“读文件 -> 写三份文档”说明。

核心状态：

- `INTAKE_STARTED`
- `NEEDS_USER_INPUT`
- `NEEDS_CONTEXT`
- `READY_TO_COMPILE`
- `AWAITING_APPROVAL`
- `READY_TO_INJECT`
- `DONE`

硬门禁：

- 有 blocking questions 时，只能提问并把 intake notes 暂存在当前对话上下文；
- 有 required context actions 时，必须先补上下文；
- 未到 `READY_TO_COMPILE`，不得生成正式 `FIRST_PROMPT.md`；
- intake notes 不得写成 `INTAKE.md` 或同类草稿文件，只能暂存在对话上下文；
- 用户未批准前，不得 clear context 和注入。

### 3.3 工具层

`scripts/pre_vibe.py` 是 deterministic helper，不负责写最终正文。

主要能力：

- `route_intake()`：分类、强度、语言、风险、不确定性、下一状态；
- `safe_walk()`：allowlist 项目扫描；
- `inspect_codex_environment()`：Codex home、AGENTS、plugin cache、marketplace 检查；
- `determine_next_state()`：根据问题、动作、证据决定状态；
- `write_artifacts()`：写入 LLM 已经定制生成的 artifact 内容，并做基础 redaction。

`scripts/mcp_server.py` 以 stdio MCP 形式暴露：

- `classify_intake`
- `scan_project_safe`
- `inspect_codex_environment`
- `write_pre_vibe_artifacts`

这让 Codex 可以把 pre-vibe 当作 workflow 能力使用，而不是让用户手动运行 Python CLI。

## 4. 三份文档的职责边界

### `PRE_VIBE_SPEC.md`

面向用户，尤其是 beginner / junior builder。它是项目 handbook，不是执行 prompt。

应包含：

- 原始输入；
- 标准化目标；
- 背景和使用场景；
- scope / out of scope；
- 功能和非功能需求；
- 验收标准；
- 项目和环境证据；
- 假设、未知项、风险；
- 初级用户能理解的建议、路径指引和下一步说明。

### `INIT_AGENTS.md`

面向 Codex。它只包含长期可复用的项目规则。

应包含：

- 全局/项目 AGENTS 摘要；
- 项目命令、目录规则、安全边界；
- 与更高优先级指令的冲突处理；
- review 和验证习惯。

不得包含本次一次性任务细节和用户教育内容。

### `FIRST_PROMPT.md`

面向 pre-vibe 清理上下文后的新 Codex session。它是唯一默认注入内容。

应只包含：

- Goal；
- Current Task；
- Hard Constraints；
- Key Assumptions；
- Relevant Context；
- Done When；
- Operating Mode。

不得包含完整 SPEC、扫描日志、source 摘要、brainstorm 历史或教程文本。

## 5. 三档强度

| 强度 | 适用 | 行为 |
|---|---|---|
| `mini` | 一般事务、小研究、轻微修改 | 最多 3 个 blocking questions，不默认 scan/fetch。 |
| `default` | 普通研究和 coding | 最多 5 个 blocking questions，轻量 allowlist scan，按需 fetch。 |
| `architect` | 新项目、重构、复杂研究、高风险任务 | 最多 10 个 blocking questions，分阶段澄清，更广扫描和检索。 |

这三个档位控制 workflow 工作量，不再作为严格 token budget。v0.3 的 token 策略是：完整信息落盘，首轮只注入最小可执行上下文。

## 6. 公开分发结构

```text
pre-vibe-plugin/
  .codex-plugin/plugin.json
  .mcp.json
  LICENSE
  README.md
  scripts/
    pre_vibe.py
    mcp_server.py
  skills/pre-vibe/
    SKILL.md
    agents/openai.yaml
    references/
```

旧的测试脚本、A/B 报告、模拟报告、缓存和系统文件不再进入分发包。

## 7. 验证与部署状态

已完成：

- 工作区插件验证通过：`validate_plugin.py pre-vibe-plugin`
- 部署目录插件验证通过：`validate_plugin.py ~/plugins/pre-vibe`
- personal marketplace 已指向 `./plugins/pre-vibe`
- 部署目录版本：`0.3.1+codex.20260606090140`
- 部署目录已清理 `.DS_Store`、`__pycache__`、旧 `tests/`

未做：

- 未新增自动化测试代码，因为本轮要求由用户进行真实场景测试。

## 8. Code Review 结果

本轮已按公开项目和可分发插件标准完成 review。

已验证：

- `git diff --check` 无 whitespace/error 输出。
- `pre_vibe.py` 和 `mcp_server.py` 语法编译通过，bytecode 输出到临时目录，未污染包体。
- 工作区插件和部署目录插件均通过 `validate_plugin.py`。
- `plugin.json` 未使用 validator 不支持的 `hooks` 字段。
- 工作区和部署目录均无 `.DS_Store`、`__pycache__`、`*.pyc`。
- 源码包和 `~/plugins/pre-vibe` 部署包 `diff -qr` 无差异。
- 桌面逆向模糊请求会进入 `NEEDS_USER_INPUT`，要求目标路径和授权，不会直接生成最终 prompt。
- AI 简历优化网站 MVP 请求会进入 `NEEDS_USER_INPUT`，先询问核心流程、数据/账号/API 边界和交付标准。
- artifact rules 明确禁止模板语言、占位符和与插件内部组件相关的最终文档表述。
- intake 草稿不会作为 `INTAKE.md` 或 `PRE_VIBE_INTAKE.md` 写入磁盘。
- `INIT_AGENTS.md` 规则要求参考全局 AGENTS.md 且不得冲突。

剩余真实场景风险：

- Codex 是否在所有新 session 中自然触发，仍取决于当前 Codex plugin/skill 调用机制；v0.3 已通过 `allow_implicit_invocation`、plugin 描述和 MCP companion 最大化贴近自动 intake。
- 三份最终文档的实际质量需要通过用户真实场景测试确认，因为本轮按要求没有新增自动化测试代码。

结论：v0.3.1 已经从“Python 文本生成器”变成“Codex workflow plugin + 状态机门禁 + 安全上下文工具层”的架构。下一步应通过真实 Codex session 验证自然触发、内置提问 UI、询问/扫描停顿、三份文档定制写作和 clear-context 后注入体验。
