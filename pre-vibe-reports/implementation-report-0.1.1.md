# pre-vibe v0.1.1 实现报告

## 目标

实现 PRD 第 21 条中的 token 优化方案，并将 plugin 整理为可公开发布的本地包体。

## 已实现

- 增加硬 token budget 模式：`micro`、`standard`、`deep`、`architect`。
- 增加压缩等级：`terse`、`balanced`、`full`、`auto`。
- 默认输出改为三个大写 Markdown 文件：
  - `PRE-VIBE-SPEC.MD`
  - `INIT-AGENTS.MD`
  - `FIRST-PROMPT.MD`
- 分离 handbook 与注入上下文：默认只注入 `FIRST-PROMPT.MD`。
- 增加显式 `/clear` 批准 handoff。
- 为生成的项目级规则增加全局 Codex `AGENTS.md` 感知。
- 增加 `final-answer-only` benchmark 模式。
- 增加离线 coding workflow 模拟。
- 增加 package README 和 MIT license。
- reports 保持在 plugin 源包体外。

## Token 证据

当前确定性离线对比和模拟报告是本轮数据来源：

- `comparison-report.md`：raw prompt vs. 完整 artifacts vs. `FIRST-PROMPT.MD`。
- `coding-workflow-simulation.md`：单 coding 场景 workflow 与 token budget。

最新离线对比：

| 场景 | Raw tokens | FIRST-PROMPT tokens | 完整 artifact tokens | Readiness delta |
|---|---:|---:|---:|---:|
| general | 12 | 382 | 1184 | +22 |
| research | 17 | 452 | 1334 | +22 |
| coding | 15 | 446 | 1327 | +22 |

最新单 coding workflow 模拟：

- `FIRST-PROMPT.MD`：约 432 tokens。
- 预算：1800 tokens。
- 结果：PASS。

v0.1.1 的关键结论不是“pre-vibe 一定降低前置 token”，而是更窄、更可测：正式 workflow 的注入内容被预算约束、足够紧凑，并与更完整的 handbook artifacts 分离。

## 验证

验证命令：

```bash
python3 -m unittest discover -s pre-vibe-plugin/tests
python3 -m compileall pre-vibe-plugin/scripts pre-vibe-plugin/tests
python3 /Users/kimfischer99/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py pre-vibe-plugin
python3 pre-vibe-plugin/scripts/run_comparison_tests.py --project . --output pre-vibe-reports/comparison-report.md
python3 pre-vibe-plugin/scripts/simulate_coding_workflow.py --project . --output-dir pre-vibe-reports/simulations/coding --report pre-vibe-reports/coding-workflow-simulation.md
```

部署验证记录在 `plugin-review.md`。

## 下一步

后续建议重新跑一轮 live A/B/C benchmark：

1. 不使用 pre-vibe。
2. 使用旧版 context-expanding pre-vibe。
3. 使用 v0.1.1 budgeted pre-vibe。

指标应跟踪“每个被接受结果的总 session tokens”，而不只看执行前 token。
