# pre-vibe v0.1.2 修复报告

## 背景

测试 session 中的原始指令是：

```text
我要逆向一个桌面上的这个东西，我要用上pre-vibe
```

旧行为会生成泛化的三份文件，内容更像插件自述，与“逆向桌面目标”关系很弱。根因是生成器没有把“逆向/桌面/这个东西”识别为目标缺失的 reverse/coding intake，也没有把目标路径、授权边界和最小识别动作作为 blocking context。

## 已修复

- 将 `逆向`、`反编译`、`反汇编`、`拆包`、`reverse`、`decompile`、`disassemble` 纳入 coding 场景识别。
- 对“桌面上的这个东西/this thing on desktop”且没有明确路径的任务，优先生成 blocking question：
  - 目标绝对路径；
  - 文件/应用名；
  - 文件类型；
  - 用户是否有权分析。
- 目标路径缺失时不扫描当前 repo，避免把无关项目上下文塞进三份文件。
- `PRE-VIBE-SPEC.MD` 新增：
  - 上下文获取动作；
  - Codex 推荐工作流与设置；
  - 缺失工具与环境建议。
- `FIRST-PROMPT.MD` 明确要求用户先查看/修改，再批准 `/clear` 和注入。
- skill 用户可见话术降噪：普通进度更新不再反复说 plugin/skill 名称，而使用“整理上下文”“准备首轮上下文”“生成预备文件”等原生 workflow 语言。

## Codex 文档依据

已通过 `openai-docs` skill 拉取官方 Codex manual 到本地缓存，并参考：

- Best practices：首轮 prompt 应包含 Goal、Context、Constraints、Done when。
- Prompting：复杂任务应拆小、可验证；模糊任务先 plan 或采访用户。
- AGENTS.md：长期规则放入全局/项目级 AGENTS，任务细节不污染长期规则。
- MCP/config：外部资料、工具和环境设置应通过 `config.toml`、MCP、sandbox/approval 等机制配置。

## 验证

命令：

```bash
python3 -m unittest discover -s pre-vibe-plugin/tests
python3 -m compileall pre-vibe-plugin/scripts pre-vibe-plugin/tests
python3 /Users/kimfischer99/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py pre-vibe-plugin
python3 pre-vibe-plugin/scripts/pre_vibe.py --task "我要逆向一个桌面上的这个东西，我要用上pre-vibe" --project . --output-dir /tmp/pre-vibe-desktop-repro --json
```

结果：

- 单测：6 tests OK。
- compileall：通过。
- plugin validation：通过。
- 复现输出：`FIRST-PROMPT.MD` 约 532 tokens，预算 1800；输出优先询问桌面目标路径和授权，不扫描当前 repo，并给出最小识别工具建议。
