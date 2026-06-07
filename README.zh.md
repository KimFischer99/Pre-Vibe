# Pre-Vibe

[![Version](https://img.shields.io/badge/version-v0.1.1-brightgreen)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Pre-Vibe 是一个 Codex 插件，用来在新会话真正开始执行前，先把用户粗略的第一句话整理成项目专属启动上下文、关键问题、AGENTS.md 兼容指引和紧凑的执行提示。

它面向刚开始使用 Codex 的用户、初级 builder，以及需求还短小、模糊、缺少执行细节的新项目会话。Pre-Vibe 会读取安全范围内的项目上下文，检查 Codex 指引，只询问真正阻塞的问题，写入项目启动文档，并在用户确认后通过 `FIRST_PROMPT.md` 交接。

## 安装

最适合新手的方式，是直接对 Codex 说：

```text
帮我把 KimFischer99/Pre-Vibe 这个插件安装到 Codex。
```

Codex 可以替你执行安装命令，并解释每一步的作用。如果你已经熟悉 Codex plugin 命令，也可以直接运行：

```bash
codex plugin marketplace add KimFischer99/Pre-Vibe --sparse .agents/plugins --sparse plugins/pre-vibe && codex plugin add pre-vibe@pre-vibe
```

安装后开启新的 Codex thread，打开 **Plugins**，启用 **Pre-Vibe**。

## 快速开始

1. 在需要整理上下文的项目目录打开 Codex。
2. 从插件选框启用 **Pre-Vibe**。
3. 输入一句粗略需求，例如“帮我把这个想法整理成可执行开发计划”。
4. 如果 Codex 打开原生问题弹窗，直接在弹窗中回答。
5. 查看生成的项目启动文档。
6. 确认交接后，让 Codex 从 `FIRST_PROMPT.md` 继续执行。

## 生成内容

Pre-Vibe 会在当前项目写入任务专属 Markdown：

- `PRE_VIBE_SPEC.md`：面向初级用户的项目 handbook，包含目标、范围、项目语言、证据、验收标准、风险和下一步。
- `AGENTS.md`：当项目没有根级 agent 指引时创建。
- `PROJECT_AGENTS.md`：当项目已有根级 `AGENTS.md` 时，作为可审校的合并建议创建。
- `FIRST_PROMPT.md`：给 Codex 的紧凑执行契约，每次交接都会完整重写。
- `PROJECT_INDEX.md`：仅 architect 档生成，用于索引项目意图、资源、工具、文件、环境和目的。

`PRE_VIBE_SPEC.md`、agent 指引文档和 `PROJECT_INDEX.md` 保持职责独立。`FIRST_PROMPT.md` 可以引用 Codex 接手时必须读取的文件。

## 强度档位

Pre-Vibe 可以自动判断强度，也允许用户通过插件设置工具调整。

- `mini`：普通小任务，最多 3 个阻塞问题。
- `default`：常规研究或代码任务，最多 5 个阻塞问题。
- `architect`：新产品、重构或高不确定性任务，最多 10 个阻塞问题，并生成 `PROJECT_INDEX.md`。

可设置项：

- 默认强度：`auto`、`mini`、`default`、`architect`
- 当前会话强度覆盖
- architect 档是否生成项目索引
- 是否允许自动升级强度
- 是否读取 Codex 环境状态

## 工作流

Pre-Vibe 的会话启动流程：

1. 检测已有 Pre-Vibe 文档、AGENTS.md 文件和 git 状态。
2. 建立安全的项目索引和 Codex 环境索引。
3. 确定强度档位和文档输出计划。
4. 通过原生 UI 询问尚未解决的阻塞决策。
5. 捕获本地和在线证据，写入 `PRE_VIBE_SPEC.md`。
6. 构建定制化启动文档。
7. 请求用户确认 `FIRST_PROMPT.md` 交接。
8. 用户确认后，读取并注入 `FIRST_PROMPT.md` 作为执行契约。

生成文档只是准备阶段，不是完成状态。只有用户确认交接并且 Codex 从 `FIRST_PROMPT.md` 继续执行，或者用户明确取消，本轮 Pre-Vibe 才算结束。

## 架构

插件包位于 `plugins/pre-vibe/`，包含：

- `.codex-plugin/plugin.json`：插件 manifest
- `.mcp.json`：内置 stdio MCP server 注册
- `skills/pre-vibe-workflow/SKILL.md`：插件内工作流指引
- `scripts/mcp_server.py`：MCP 工具入口
- `scripts/pv_*.py`：路由、扫描、提问、设置、文档和压缩输出模块

MCP server 只向用户展示短状态，把详细工作流数据交给 Codex。Python 层负责确定性路由、校验、扫描、设置和安全写入；最终任务专属 Markdown 由 Codex 根据用户输入和项目证据写作。

## 文件结构

```text
pre-vibe/
├── .agents/plugins/marketplace.json
├── docs/
│   ├── installation.md
│   ├── privacy.md
│   ├── quickstart.md
│   ├── troubleshooting.md
│   └── workflow.md
├── plugins/pre-vibe/
│   ├── .codex-plugin/plugin.json
│   ├── .mcp.json
│   ├── README.md
│   ├── scripts/
│   └── skills/pre-vibe-workflow/SKILL.md
├── tests/
├── CHANGELOG.md
├── CONTRIBUTING.md
├── PRIVACY.md
└── README.md
```

## 文档

- [安装](docs/installation.md)
- [快速开始](docs/quickstart.md)
- [工作流契约](docs/workflow.md)
- [故障排查](docs/troubleshooting.md)
- [隐私](PRIVACY.md)

## 开发检查

```bash
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/pre-vibe
python3 -m py_compile plugins/pre-vibe/scripts/*.py
python3 -m unittest discover -s tests
codex review --uncommitted
```

## 安全

Pre-Vibe 使用 allowlist 项目扫描，跳过疑似敏感文件，把输出路径限制在当前项目内，并避免静默覆盖已有根级 `AGENTS.md`。

## 许可证

MIT
