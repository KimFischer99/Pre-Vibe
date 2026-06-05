# pre-vibe v0.1.1 架构与测试报告

## 摘要

v0.1.1 落实了 PRD 第 21 条的修正：pre-vibe 现在是带硬 token budget 的 context optimizer，而不是默认扩大上下文的 context expander。

插件现在生成：

- `PRE-VIBE-SPEC.MD`：用户可查看/修改的 handbook，默认不注入。
- `INIT-AGENTS.MD`：结合全局 Codex `AGENTS.md` 的项目级 AGENTS 建议。
- `FIRST-PROMPT.MD`：紧凑执行 brief，唯一默认注入上下文。

## 已实现改动

| 模块 | v0.1.1 行为 |
|---|---|
| 任务 intake | 路由 `general`、`research`、`coding` 和 `mixed` 任务。 |
| 预算控制 | 增加 `micro`、`standard`、`deep`、`architect` 硬预算。 |
| 压缩控制 | 增加 `terse`、`balanced`、`full` 和 `auto`。 |
| 上下文策略 | 使用文件/source 指针，而不是长摘要。 |
| workflow handoff | 要求用户 review、批准 `/clear`，并只注入 `FIRST-PROMPT.MD`。 |
| AGENTS 处理 | 读取全局 Codex `AGENTS.md`，并生成不冲突的项目级建议。 |
| Benchmark | 增加 `final-answer-only` benchmark 模式和单 coding workflow 模拟器。 |

## 测试命令

```bash
python3 -m unittest discover -s pre-vibe-plugin/tests
python3 -m compileall pre-vibe-plugin/scripts pre-vibe-plugin/tests
python3 /Users/kimfischer99/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py pre-vibe-plugin
python3 pre-vibe-plugin/scripts/run_comparison_tests.py --project . --output pre-vibe-reports/comparison-report.md
python3 pre-vibe-plugin/scripts/simulate_coding_workflow.py --project . --output-dir pre-vibe-reports/simulations/coding --report pre-vibe-reports/coding-workflow-simulation.md
```

部署验证记录在 `plugin-review.md` 中，覆盖安装到个人 plugin 源目录并重新安装后完成。

## 离线对比

确定性对比现在把“落盘完整 artifacts”和“正式注入的 `FIRST-PROMPT.MD`”分开统计。解释口径如下：

- raw prompt 在执行前 token 成本最低；
- pre-vibe 通过增加假设、约束、验收标准和文件/source 指针提升 readiness；
- 只有 `FIRST-PROMPT.MD` 应计入默认正式 workflow 注入。

当前数据见 `comparison-report.md`。

## Coding Workflow 模拟

单 coding 场景模拟验证了用户要求的 workflow 状态机：

```text
generate -> review -> approve_clear -> inject -> start_work
```

模拟检查项：

- 三个大写文件全部存在；
- `PRE-VIBE-SPEC.MD` 被作为 handbook；
- prompt 和 handoff 中都出现 `/clear` 批准步骤；
- `FIRST-PROMPT.MD` 保持在预算内；
- `INIT-AGENTS.MD` 包含全局 AGENTS 感知。

当前数据见 `coding-workflow-simulation.md`。

## 剩余限制

- 外部 reference fetching 在 v0.1.1 中表现为 source map/search plan，不在生成器内实时 fetch。
- v0.1.1 未增加 hooks，因为当前 handoff 可通过 skill/script 交互和用户显式批准完成。
- 若要宣称“单位成功结果 token 下降”，仍需要后续 live A/B/C 评估。
