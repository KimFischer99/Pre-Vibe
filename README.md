# pre-vibe v0.1.2

pre-vibe is a token-disciplined first-turn context intake compiler for agent workflows. It turns a vague task into three project-facing Markdown files:

- `PRE-VIBE-SPEC.MD` - handbook only; do not inject the full file into the formal workflow.
- `INIT-AGENTS.MD` - project-level AGENTS guidance that accounts for global Codex `AGENTS.md` when available.
- `FIRST-PROMPT.MD` - compact execution brief; the only default injected context.

The public-ready plugin package lives in `pre-vibe-plugin`. Reports and generated test artifacts live separately in `pre-vibe-reports`.

## Quick Run

```bash
python3 pre-vibe-plugin/scripts/pre_vibe.py \
  --task "帮我把这个项目整理成可以交给 agent 执行的任务" \
  --project . \
  --agent codex \
  --mode auto \
  --output-dir .
```

After generation, review or edit `PRE-VIBE-SPEC.MD` and `INIT-AGENTS.MD`. Formal work starts only after approving `/clear` and injecting `FIRST-PROMPT.MD`.

## Test

```bash
python3 -m unittest discover -s pre-vibe-plugin/tests
python3 /Users/kimfischer99/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py pre-vibe-plugin
python3 pre-vibe-plugin/scripts/run_comparison_tests.py --output pre-vibe-reports/comparison-report.md
python3 pre-vibe-plugin/scripts/simulate_coding_workflow.py --project . --report pre-vibe-reports/coding-workflow-simulation.md
```

Live Codex A/B checks are available but intentionally separate because they consume real model tokens:

```bash
python3 pre-vibe-plugin/scripts/run_live_codex_ab.py --project . --output-dir pre-vibe-reports/live
```
