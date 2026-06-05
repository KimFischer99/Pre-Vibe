# pre-vibe Coding Workflow 模拟报告

本报告是对要求中的 pre-vibe workflow 做离线模拟。未调用 live model。

## 场景

- 任务：根据当前项目 PRD，为 pre-vibe plugin 增加 token budget、精简 first prompt，并更新测试。
- 场景：coding
- 复杂度：standard
- 压缩等级：balanced
- `FIRST-PROMPT.MD` token 估算：432
- 预算：1800

## Workflow 状态

- generate：pre-vibe 生成三个大写 Markdown 文件。
- review：用户查看 handbook 和 init agents guidance。
- approve_clear：用户批准正式 workflow 前执行 `/clear`。
- inject：只将 `FIRST-PROMPT.MD` 注入为初始上下文。
- start_work：agent 基于短计划和受控上下文开始工作。

## 检查结果

- three_files：PASS
- uppercase_names：PASS
- spec_not_in_prompt：PASS
- clear_handoff：PASS
- prompt_under_budget：PASS
- agents_mentions_global：PASS
- spec_is_handbook：PASS

## 生成文件

- Spec handbook：`pre-vibe-reports/simulations/coding/PRE-VIBE-SPEC.MD`，约 614 tokens。
- Init agents：`pre-vibe-reports/simulations/coding/INIT-AGENTS.MD`，约 251 tokens。
- First prompt：`pre-vibe-reports/simulations/coding/FIRST-PROMPT.MD`，约 432 tokens。

## Handoff

```text
NEXT STEP
1. 请用户查看/修改 `pre-vibe-reports/simulations/coding/PRE-VIBE-SPEC.MD` 和 `pre-vibe-reports/simulations/coding/INIT-AGENTS.MD`。
2. 询问用户：是否批准执行 `/clear` 并将 FIRST-PROMPT.MD 作为新 session 初始上下文注入？
3. 用户批准后，只注入 `pre-vibe-reports/simulations/coding/FIRST-PROMPT.MD`，不要注入完整 spec。
4. FIRST-PROMPT token estimate: 432; budget: 1800.
```

## 结论

PASS
