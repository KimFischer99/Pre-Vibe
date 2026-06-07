# Pre-Vibe

[![Version](https://img.shields.io/badge/version-v0.1.3-brightgreen)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Pre-Vibe 把你的粗略需求整理成 **三份结构化文档**，让 Claude Code 每次开始工作前都有清晰的范围、项目上下文和执行契约。它安全读取项目文件，只问真正必要的问题，然后用一份紧凑的 FIRST_PROMPT.md 交付给 Claude Code 开始工作。

> 适合刚接触 Claude Code 的新手、面向初级 builder、以及需求短小模糊、缺少执行细节的早期产品会话。

---

## 安装指引

```bash
claude plugin marketplace add KimFischer99/CC-Pre-Vibe
claude plugin install pre-vibe@pre-vibe
```

Claude Code 会自动处理克隆、缓存和更新，无需手动 `git clone`、`git pull` 或编辑 settings JSON。

安装完成后重启 Claude Code，输入 `/pre-vibe`，然后描述你的任务即可。

---

## 快速开始

| 步骤 | 你做什么 | Claude Code 做什么 |
|------|---------|-------------------|
| **1.** 输入 `/pre-vibe` | 描述你的粗略需求 | 插件激活，安全扫描项目 |
| **2.** 回答问题 | 在原生弹窗中选择答案 | 只问必要的范围澄清问题 |
| **3.** 审核文档 | 检查 PRE_VIBE_SPEC.md、CLAUDE.md、FIRST_PROMPT.md | 写入三份任务专属文件 |
| **4.** 确认交接 | 确认 FIRST_PROMPT.md 符合预期 | 执行 `/clear` → 注入 FIRST_PROMPT.md → 开始实际工作 |

---

## 三份文档：三份工程约束

Pre-Vibe 生成三份任务专属文档，共同约束 Claude Code 的上下文、降低幻觉、提升实现精准度：

| 文档 | 做什么 | 为什么重要 |
|---|---|---|
| `PRE_VIBE_SPEC.md` | 工程执行手册——环境变量、技术栈、已安装插件和 skills、项目组件清单、git 状态、集成建议 | 在写代码之前，用项目实际状态（而非背景百科）对齐 Claude Code 的认知 |
| `CLAUDE.md`（或 `PROJECT_CLAUDE.md`） | Claude Code 执行规则——约束、指针、边界、验证要求 | Claude Code 每次启动自动加载，防止跑偏，保证输出质量 |
| `FIRST_PROMPT.md` | 紧凑执行契约——Completion Contract、停止条件、验证门 | 交接后唯一的提示词，让 Claude Code 始终聚焦交付物 |

> **architect** 档位还会生成 `PROJECT_INDEX.md`，索引项目意图、资源、工具、环境和目的。

三份文档共同作用，**约束大模型上下文、减少幻觉、确保 Claude Code 始终不偏离交付目标**——对非英语提示、复杂项目、或 token 预算紧张的会话尤其有效。

---

## 强度档位

| 档位 | 问题数 | 适合 |
|-------|--------|------|
| **mini** | ≤ 3 | 小改动、快速修复、简单查询 |
| **default** | ≤ 5 | 常规开发或研究任务 |
| **architect** | ≤ 10 + PROJECT_INDEX.md | 新产品、重构、高不确定性工作 |

随时通过插件设置调整，或使用 `set_effort_level` 工具。

---

## 工作流程

1. 检测已有 Pre-Vibe 文档、CLAUDE.md 文件、环境变量、已安装插件/skills、git 状态、过往 session 上下文
2. 建立安全项目索引（跳过密钥、node_modules 等）
3. 确定强度档位和文档输出计划
4. 弹出原生问题选择框
5. 写入工程执行聚焦的定制化启动文档
6. 展示 FIRST_PROMPT.md 供用户审计 → 用户确认后执行 `/clear` 并注入执行契约

Pre-Vibe 的 MCP 工具通过 `CLAUDE_PROJECT_DIR` 解析默认项目根目录；该变量由 Claude Code 指向当前会话的项目根。显式传入的 `project` 或 `project_root` 参数仍然优先。

---

## 架构

```
plugins/pre-vibe/
├── .claude-plugin/plugin.json     # 插件清单
├── .mcp.json                      # stdio MCP 服务器
├── skills/pre-vibe/SKILL.md       # 工作流指引
├── scripts/
│   ├── mcp_server.py              # MCP 工具入口
│   ├── pre_vibe.py                # CLI / 兼容入口
│   ├── pv_*.py                    # 路由、扫描、提问、设置、输出
│   └── pyproject.toml             # Python 项目配置
└── README.md
```

Python 层负责确定性路由、扫描、校验和安全写入；最终的三份 Markdown 由 Claude Code 根据项目实际上下文写作。

`scripts/pre_vibe.py` 是面向开发者的 CLI / 兼容入口：它保持 MCP server 依赖的旧导入面稳定，也可用于本地检查路由，例如：`python3 plugins/pre-vibe/scripts/pre_vibe.py --task "fix login" --project . --no-scan`。

---

## 文档

- [快速开始](docs/quickstart.md)
- [工作流契约](docs/workflow.md)
- [安装](docs/installation.md)
- [故障排查](docs/troubleshooting.md)
- [隐私与安全](PRIVACY.md)

---

## 安全

- Allowlist 扫描——只读取安全文件名和后缀
- 自动跳过密钥、Token、数据库、日志等敏感文件
- 输出路径限在项目内
- 绝不静默覆盖已有的根级 `CLAUDE.md`；改用 `PROJECT_CLAUDE.md` 或在明确确认后替换

---

## 开发

```bash
claude plugin validate plugins/pre-vibe --strict
python3 -m py_compile plugins/pre-vibe/scripts/*.py
python3 -m unittest discover -s tests
```

## 许可证

MIT
