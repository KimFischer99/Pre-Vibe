# pre-vibe v0.1.1 架构报告

## 产品定位

pre-vibe 是一个面向 agent workflow 的首轮上下文 intake compiler，并且以 token discipline 为核心约束。一般事务、研究任务、代码开发是同一产品定位下的三类任务 intake 策略，不是三个不同产品定位。

v0.1.1 的关键变化是从“context expander”转向“context optimizer”：

```text
模糊用户输入
  -> 带预算的 intake package
  -> handbook + 项目规则建议落盘
  -> 用户批准后只注入紧凑 FIRST-PROMPT
```

## 包体结构

公开 plugin 源文件与报告文件已分离：

```text
pre-vibe-plugin/
  .codex-plugin/plugin.json
  README.md
  LICENSE
  skills/pre-vibe/SKILL.md
  skills/pre-vibe/references/
  scripts/pre_vibe.py
  scripts/run_comparison_tests.py
  scripts/run_live_codex_ab.py
  scripts/simulate_coding_workflow.py
  tests/test_pre_vibe.py

pre-vibe-reports/
  architecture.md
  reference-analysis.md
  comparison-report.md
  coding-workflow-simulation.md
```

## 运行流程

1. 将任务分类为 `general`、`research`、`coding` 或 `mixed`。
2. 选择硬预算：`micro`、`standard`、`deep` 或 `architect`。
3. 只扫描该预算允许的安全项目上下文。
4. 非阻塞未知项转为显式假设；只提出会改变执行路径的 blocking questions。
5. 生成三个大写 Markdown 文件：
   - `PRE-VIBE-SPEC.MD`：只作为 handbook，不作为默认注入上下文。
   - `INIT-AGENTS.MD`：结合全局 Codex `AGENTS.md` 的项目级 AGENTS 建议。
   - `FIRST-PROMPT.MD`：紧凑执行 brief，也是唯一默认注入上下文。
6. 让用户查看或修改前两个文件。
7. 直到用户批准 `/clear` 并只注入 `FIRST-PROMPT.MD`，pre-vibe workflow 才结束。

## Token Budget 模型

| 模式 | 适用场景 | 上下文策略 | 注入预算 |
|---|---|---|---:|
| `micro` | 日常/一般事务 | 不扫描、不 fetch、不提问 | 800 |
| `standard` | 普通研究/代码任务 | 轻量扫描，最多 3 个问题 | 1800 |
| `deep` | 多文件代码/spec 任务 | 更广扫描，最多 6 个问题 | 3500 |
| `architect` | 新项目/重构/系统设计 | 分阶段 workflow | 6000 |

压缩等级独立控制为 `terse`、`balanced` 或 `full`，`auto` 会根据预算自动映射。

## 安全模型

扫描器默认跳过 secret-like 文件：`.env`、私钥、token/credential 路径、本地数据库、dump 和 log。被跳过的文件名会记录在 handbook 中，让用户知道相关但敏感的上下文被有意排除。

`INIT-AGENTS.MD` 不会替代全局 Codex 指令。它会在可用时摘要全局 `AGENTS.md`，补充项目级长期规则，并包含冲突处理策略：全局/个人规则优先级始终高于生成的项目建议。

## 评估模型

v0.1.1 使用三类轻量检查：

- 单元测试：覆盖任务分类、输出命名、secret 跳过、micro budget 行为和全局 AGENTS 感知。
- 确定性离线对比：估算 token 并计算 readiness 分数。
- 离线 coding workflow 模拟：验证 generate -> review -> approve_clear -> inject -> start_work 流程。

Live Codex A/B 测试仍然可用，但它会消耗真实模型 token，因此保留为独立流程，并应使用 `final-answer-only` benchmark 模式。
