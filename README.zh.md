# Pre-Vibe

[![Version](https://img.shields.io/badge/version-v0.1.2-brightgreen)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Pre-Vibe 把一句粗略的需求帮你整理成 **三份结构化文档**，让 Claude Code 每次开始工作时都有清晰的范围、项目上下文和执行契约。它安全读取项目文件，只问真正必要的问题，然后用一份紧凑的提示（`FIRST_PROMPT.md`）交付给 Claude Code 开始工作。

> 尤其适合刚接触 Claude Code 的新手、早期产品需求、以及提示词短小模糊、缺少执行细节的会话。

---

## 一句话安装

在 Claude Code 中直接输入：

```
帮我安装一下这个 plugin：KimFischer99/CC-Pre-Vibe
```

或手动安装：

```bash
# 1. 添加市场（只需一次）
claude plugin marketplace add https://raw.githubusercontent.com/KimFischer99/CC-Pre-Vibe/main/.claude-plugin/marketplace.json

# 2. 打开自动更新
claude plugin marketplace auto-update --enable pre-vibe

# 3. 安装插件
claude plugin install pre-vibe@pre-vibe
```

重启 Claude Code，输入 `/pre-vibe`，然后说出你的粗略需求。

---

## 快速开始（3 分钟）

| 步骤 | 操作 |
|------|------|
| **1.** 在 Claude Code 中输入 `/pre-vibe` | 插件激活 |
| **2.** 说出你的粗略需求 | 例如 "帮我整理一个开发计划" |
| **3.** 回答 2-5 个关键问题 | Claude Code 自动弹出原生问题选择框 |
| **4.** 查看生成的文档 | 三份文件出现在项目目录 |
| **5.** 确认交接 | `/clear` → 注入 FIRST_PROMPT.md → 正式开始工作 |

---

## 三份文档，三步精准约束

Pre-Vibe 生成三份任务专属文档，共同约束 Claude Code 的上下文、降低幻觉、提升实现精准度：

| 文档 | 作用 | 为什么重要 |
|---|---|---|
| `PRE_VIBE_SPEC.md` | 项目手册——目标、范围、术语定义、证据、验收标准、风险 | 在写代码之前，统一 Claude Code 对你需求的认知，避免鸡同鸭讲 |
| `CLAUDE.md`（或 `PROJECT_CLAUDE.md`） | Claude Code 执行规则——约束、指针、边界、验证要求 | Claude Code 每次启动自动读取，防止跑偏，保证输出质量 |
| `FIRST_PROMPT.md` | 紧凑执行契约——Completion Contract、停止条件、验证门 | 交接后唯一的提示词，让 Claude Code 始终聚焦交付物，不重读历史 |

> **architect** 档位还会生成 `PROJECT_INDEX.md`，索引项目意图、资源、工具、环境和目的。

这三份文档共同作用，**约束大模型上下文、减少幻觉、确保 Claude Code 始终不偏离交付目标**——对非英语提示、复杂项目、或 token 预算紧张的会话尤其有效。

---

## 强度档位

| 档位 | 问题数 | 适用场景 |
|-------|--------|----------|
| **mini** | ≤ 3 | 小改动、快速修复、简单查询 |
| **default** | ≤ 5 | 常规开发或研究任务 |
| **architect** | ≤ 10 + PROJECT_INDEX.md | 新产品、重构、高不确定性工作 |

随时通过插件设置调整：
- 默认强度：`auto`、`mini`、`default`、`architect`
- 当前会话强度覆盖
- architect 档是否生成项目索引
- 自动升级行为
- Claude Code 环境读取开关

---

## 工作流程

1. 检测已有 Pre-Vibe 文档、`CLAUDE.md` 文件和 git 状态
2. 建立安全项目索引（跳过密钥、`node_modules` 等）
3. 确定强度档位和文档输出计划
4. 弹出原生问题选择框，询问阻塞问题
5. 写入定制化的项目启动文档
6. 请求用户确认 → `/clear` → 注入 `FIRST_PROMPT.md` 作为执行契约

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

Python 层负责确定性路由、扫描、校验和安全写入；最终的三份 Markdown 由 Claude Code 根据用户输入和项目证据写作。

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
- 输出路径限在项目内，不会写到项目以外
- 绝不会静默覆盖已有的根级 `CLAUDE.md`

---

## 开发

```bash
claude plugin validate plugins/pre-vibe
python3 -m py_compile plugins/pre-vibe/scripts/*.py
python3 -m unittest discover -s tests
```

## 许可证

MIT
