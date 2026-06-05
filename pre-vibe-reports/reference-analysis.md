# 参考项目分析

## 范围

参考仓库已 clone 到 `/private/tmp/pre-vibe-reference-projects` 进行本地分析：

- `linshenkx/prompt-optimizer`
- `ckelsoe/prompt-architect`

本次分析目标不是复制它们的产品模型，而是识别可让 pre-vibe 更可用的实现模式，同时保留 pre-vibe 面向 agent workflow 的定位。

## prompt-optimizer

值得借鉴的模式：

- 将 prompt 工作视为资产生命周期：优化、测试、比较、保存、复用。
- 支持多入口：web、desktop、extension、Docker 和 MCP。
- 显式展示 template 选择，让用户知道正在使用哪种优化方式。
- 提供 evaluation/comparison workflow，而不只依赖“看起来更好”的主观判断。

pre-vibe 不应照搬的部分：

- 不要变成通用 text-to-text prompt optimizer。
- 当 agent 已经可以读取本地项目文件时，不要默认生成很长的 optimized prompt。
- 不要把生成报告混进 plugin 源包体。

v0.1.1 已吸收：

- 分离 package source 和 reports。
- 保留确定性 comparison tests。
- 将生成上下文视为可复用落盘 artifacts，但正式只注入 compact brief。

## prompt-architect

值得借鉴的模式：

- 在选择框架前先做 intent routing。
- 从 clarity、specificity、context、completeness、structure 五个维度评估质量。
- 提出 targeted clarification questions，而不是开放式 brainstorm。
- 使用 progressive disclosure：只在需要时加载详细 framework guidance。
- 输出一个用户真的可以接着使用的 clean handoff prompt。

pre-vibe 不应照搬的部分：

- 不要把 27 个通用 prompt framework 作为产品核心。
- 不要对简单日常任务默认提出 3-5 个问题。
- 不要把完整 framework scaffold 当作正式 agent context。

v0.1.1 已吸收：

- 增加同样五个维度的轻量 quality scoring。
- 增加场景感知的 intake 与 budget routing。
- 增加 blocking-question 逻辑，并让 `micro` 模式不提问。
- 保持 skill guidance 短小，把细节移入 reference files。

## 产品含义

pre-vibe 的正确差异化是：

```text
prompt optimizer: 改进 prompt 文本
prompt architect: 选择并应用 prompt framework
pre-vibe: 为 agent workflow 准备最小必要首轮上下文
```

这保留了 PRD 第 20 条中的产品重点：pre-vibe 解决的是 agent workflow 中的环境、项目和用户需求信息差，而不是单纯让 prompt prose 更漂亮。
