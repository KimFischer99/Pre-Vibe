# Pre-Vibe

Pre-Vibe 是一个 Codex 插件，用来在真正执行任务前，把用户粗略的首轮描述整理成稳定、清晰、适合 Codex 开工的项目启动上下文。

它面向刚开始使用 Codex 的用户、初级 builder，以及需求还短小、模糊、缺少执行细节的新项目会话。Pre-Vibe 不会让 Codex 直接进入实现，而是先读取安全范围内的项目上下文，澄清真正阻塞的问题，构建定制化项目初始文档，并在用户确认后只注入压缩后的首轮提示。

Pre-Vibe 是插件包，不是 bundled skill，也不是命令式 prompt 工作流。

## 安装

```bash
codex plugin marketplace add KimFischer99/Pre-Vibe --sparse .agents/plugins --sparse plugins/pre-vibe && codex plugin add pre-vibe@pre-vibe
```

安装后开启新的 Codex thread，打开 **Plugins**，确认 **Pre-Vibe** 已启用。

## 快速开始

1. 在需要整理上下文的项目目录中打开 Codex。
2. 在插件选框中启用 **Pre-Vibe**。
3. 输入一句粗略需求，或选择 Pre-Vibe 的 starter prompt。
4. 让 Codex 先读取项目结构和 Codex 环境。
5. 如果 Codex 打开原生问题弹窗，直接在弹窗中回答。
6. 查看生成的项目启动上下文，确认后交接给正式执行阶段。

不需要输入命令。如果某个 Codex surface 暂时没有开放原生 MCP elicitation，Pre-Vibe 会说明这个限制，而不是退回冗长的普通聊天追问。

## 生成内容

Pre-Vibe 会在当前项目中写入三份定制化 Markdown 文件：

- `PRE_VIBE_SPEC.md`：面向初级用户的项目 handbook，包含目标、范围、用户流程、验收标准、风险、建议和项目路径指引。
- `PROJECT_AGENTS.md`：面向 Codex 的简洁执行规则，并且必须尊重全局 `AGENTS.md`。
- `FIRST_PROMPT.md`：用户确认后注入的压缩首轮提示。

这三份文件必须根据用户要求、项目证据、环境证据和用户回答定制写作。除非用户正在开发 Pre-Vibe 本身，否则文件内容不得出现可复用模板话术，也不得出现 Pre-Vibe 实现细节。

## 工作流

Pre-Vibe 借鉴 [github/spec-kit](https://github.com/github/spec-kit) 这类 spec-driven 工具的产品思路：先澄清结果，再保留项目原则，再规划执行边界，最后让 agent 基于稳定提示开工。但它的实现方式不同：Pre-Vibe 始终是 Codex plugin，通过 MCP companion 融合 Codex，而不是安装命令文件或 skill。

正常流程是：

1. 准备项目启动上下文。
2. 读取安全范围内的项目文件和 Codex 组件状态。
3. 对阻塞问题请求 Codex 原生提问 UI。
4. 构建项目初始文档。
5. 请求用户确认。
6. 清理工作上下文，只注入压缩首轮提示。

## 强度档位

- `mini`：普通小任务，最多 3 个阻塞问题。
- `default`：常规研究或代码任务，最多 5 个阻塞问题。
- `architect`：新产品、重构或高不确定性任务，最多 10 个阻塞问题。

这些是工作流强度档位，不是严格 token 预算。

## 仓库结构

- `.agents/plugins/marketplace.json`：Codex 安装用的 repo marketplace。
- `plugins/pre-vibe/`：可分发的 Codex 插件包。
- `plugins/pre-vibe/.codex-plugin/plugin.json`：插件 manifest。
- `plugins/pre-vibe/.mcp.json`：内置 MCP server 注册。
- `plugins/pre-vibe/scripts/pre_vibe.py`：确定性工作流工具。
- `plugins/pre-vibe/scripts/mcp_server.py`：最小 stdio MCP server。
- `architecture.md`：当前架构说明。
- `pre-vibe_PRD.md`：产品需求文档。

## 开发检查

验证插件包：

```bash
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/pre-vibe
python3 -m py_compile plugins/pre-vibe/scripts/pre_vibe.py plugins/pre-vibe/scripts/mcp_server.py
```

分发前运行 code review：

```bash
codex review --uncommitted
```

本项目不设计自动化场景测试。工作流质量应通过真实 Codex session 测试。

## 安全

Pre-Vibe 默认只做 allowlist 项目扫描，并跳过疑似敏感文件，包括环境变量文件、私钥、token 存储、数据库 dump 和生产日志。临时准备信息只保留在当前对话上下文中。

## 许可证

MIT
