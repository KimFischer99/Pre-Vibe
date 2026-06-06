# Pre-Vibe v0.5 架构报告

## 目标

Pre-Vibe 是原生 Codex Plugin 工作流，不是 bundled skill，也不是命令式 prompt 工具。它的目标是在新 Codex session 开始时，把用户短小、模糊、混乱或高风险的初始需求整理成稳定的项目启动上下文：先索引项目和 Codex 环境，再通过 Codex 原生提问 UI 澄清阻塞问题，最后生成定制化初始文档，并在用户确认后只注入压缩后的 first prompt。

本版实现版本：`0.5.0`。

## 关键决策

| 要求 | v0.5 实现 |
|---|---|
| 只保留 plugin，不经过 skill 调用 | manifest 删除 `skills` 字段，源包删除 `skills/` 目录；插件只通过 `.codex-plugin/plugin.json`、`.mcp.json` 和 MCP server 工作。 |
| 不再依赖命令式启动 | 删除 `commands/`、`prompts/` 和命令安装脚本；manifest 删除命令能力描述；启动入口改为 Codex plugin picker 与 starter prompts。 |
| 保证插件选框启动不受影响 | manifest 保留 `interface.defaultPrompt`，并通过 MCP tool schema 暴露 `prepare_project_start` 等产品动作，方便 Codex 在启用插件后自然调用。 |
| 提问不能停留在文本对话 | MCP server 新增 `open_question_dialog`，会向 Codex 客户端发送 `elicitation/create` 请求并等待返回；同时 `prepare_project_start` 返回兼容 Codex `request_user_input` 形状的结构化问题请求。 |
| 后台字段不暴露给用户 | MCP tool 的 `content.text` 只返回短状态，如“正在构建项目初始文档。”；详细状态、问题 schema、证据和写作规则放入 `structuredContent`，避免普通 session 中出现后台字段。 |
| 不直接生成模板文档 | `write_artifacts()` 只写入 Codex 已经基于用户任务和项目证据写好的内容，并做文件名与交叉引用校验。 |
| 三档强度 | `mini/default/architect` 的问题上限为 `3/5/10`；三档都做项目和 Codex 环境索引，只调整扫描深度、fetch 建议和规划深度。 |
| AGENTS 不冲突 | `PROJECT_AGENTS.md` 必须参考全局 `AGENTS.md`，不得削弱或冲突。 |
| 公开分发 | 新增 repo marketplace：`.agents/plugins/marketplace.json` 指向 `./plugins/pre-vibe`，README 提供一句话安装命令。 |

## 工作流

```text
plugin picker / starter prompt / natural request
  -> prepare_project_start
       - safe project execution index
       - Codex environment and component index
       - effort selection
  -> open_question_dialog
       - only when blocking answers remain
       - MCP elicitation first
       - request_user_input payload as compatible structured form
  -> build project starting documents
       - PRE_VIBE_SPEC.md
       - PROJECT_AGENTS.md
       - FIRST_PROMPT.md
  -> approval
  -> clear current working context
  -> inject compact first prompt
  -> plugin exits; Markdown files remain on disk
```

## 核心实现

- `plugins/pre-vibe/.codex-plugin/plugin.json`
  - 仅声明 plugin metadata 与 MCP companion。
  - 不声明 `skills`，不声明命令式启动能力。
  - `defaultPrompt` 提供插件选框启动语句。
- `plugins/pre-vibe/.mcp.json`
  - 注册 stdio MCP server：`python3 ./scripts/mcp_server.py`。
- `plugins/pre-vibe/scripts/mcp_server.py`
  - `prepare_project_start`：执行项目启动准备，返回短状态和结构化上下文。
  - `open_question_dialog`：向 Codex 发送 `elicitation/create`，尝试打开原生提问 UI。
  - `scan_project_safe`：allowlist 项目扫描，跳过 secrets、依赖、构建产物。
  - `inspect_codex_environment`：读取全局 AGENTS、enabled plugins、plugin cache、standalone skills 和 marketplace 状态。
  - `write_project_starting_documents`：写入 Codex 已生成的最终文档。
- `plugins/pre-vibe/scripts/pre_vibe.py`
  - `prepare_project_start()`：产品化入口，不暴露旧后台术语。
  - `route_intake()`：内部路由函数，保留用于状态判断和兼容。
  - `native_question_payload()`：生成 MCP elicitation 与 Codex question UI 双形态请求。
  - `write_artifacts()`：写文件和安全校验，不生成正文。

## 提问 UI 边界

当前 Codex feature 列表显示 `tool_call_mcp_elicitation` 为 stable，而 `default_mode_request_user_input` 仍未启用。因此 v0.5 采用两层策略：

1. MCP server 主动发送 `elicitation/create` 请求，这是当前版本最接近插件端原生弹窗的实现。
2. 同时返回 `request_user_input` 兼容问题结构，供支持该工具的 Codex surface 使用。

如果当前 Codex surface 不接受 MCP elicitation，插件必须返回“原生提问窗口不可用”的状态，而不是把阻塞问题改成普通聊天文本。

## 文档生成规则

`PRE_VIBE_SPEC.md` 面向用户和初级 builder。它应写成项目 handbook，包含原始需求、标准化目标、用户场景、范围、需求、验收标准、项目证据、组件建议、风险、建议和下一步。

`PROJECT_AGENTS.md` 面向 Codex。它只保留项目执行规则、命令、目录边界、安全约束、验证方式、全局 AGENTS 继承和冲突规则。

`FIRST_PROMPT.md` 是唯一默认注入内容。它必须压缩成目标、当前任务、硬约束、关键假设、相关上下文、完成标准和操作模式。

三份文件必须基于用户输入、项目证据、环境证据和用户回答定制写作。除非用户任务本身就是开发 Pre-Vibe，否则最终文档不得出现 Pre-Vibe、插件实现、MCP server 或内部工作流表述。

## 分发结构

```text
.agents/plugins/marketplace.json
plugins/pre-vibe/
  .codex-plugin/plugin.json
  .mcp.json
  LICENSE
  README.md
  scripts/
    mcp_server.py
    pre_vibe.py
```

公开安装命令：

```bash
codex plugin marketplace add KimFischer99/Pre-Vibe --sparse .agents/plugins --sparse plugins/pre-vibe && codex plugin add pre-vibe@pre-vibe
```

## 已知边界

- Codex plugin 文档明确支持插件打包 MCP servers；本版依赖 MCP tool schema 和 elicitation，而不是 skill 指令文件。
- MCP elicitation 是否呈现为弹窗取决于用户当前 Codex surface。代码已实现请求路径，但真实 UI 表现仍需通过 live Codex session 验证。
- 旧本地 cache 中的历史 Pre-Vibe skill 需要在部署阶段清理，否则旧版本缓存可能仍被某些本地索引器看到。
