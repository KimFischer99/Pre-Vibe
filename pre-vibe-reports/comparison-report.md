# pre-vibe 对比测试报告

本报告为确定性离线对比：比较原始任务 prompt 与 pre-vibe 生成的上下文包。

| 场景 | Raw tokens | FIRST-PROMPT tokens | 完整 artifact tokens | Raw readiness | pre-vibe readiness | Landing effect |
|---|---:|---:|---:|---:|---:|---|
| general | 12 | 382 | 1184 | 0 | 22 | readiness 提升 |
| research | 17 | 452 | 1334 | 2 | 24 | readiness 提升 |
| coding | 15 | 446 | 1327 | 2 | 24 | readiness 提升 |

## 解读

- Raw prompt 的前置 token 成本最低，因为没有做上下文工程。
- pre-vibe 会把三份 artifact 落盘保存，但正式 workflow 默认只注入带预算的 `FIRST-PROMPT.MD`。
- Landing effect 使用本地 readiness rubric 测量：目标、假设、验收标准、风险、验证和场景关键词。
- 在宣称真实任务完成效果提升前，仍需要 live model A/B/C 测试。
