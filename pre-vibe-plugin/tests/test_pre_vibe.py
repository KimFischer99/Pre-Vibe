import tempfile
import unittest
import sys
import os
from pathlib import Path
from types import SimpleNamespace

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from scripts.pre_vibe import build_result, classify_task, write_outputs


class PreVibeTests(unittest.TestCase):
    def make_args(self, task: str, tmp: str, scenario: str = "auto"):
        return SimpleNamespace(
            task=task,
            project=tmp,
            agent="codex",
            mode="standard",
            scenario=scenario,
            compression="auto",
            language="auto",
            benchmark_mode="execution",
            output_dir=tmp,
            json=False,
        )

    def test_classifies_three_primary_scenarios(self):
        self.assertEqual(classify_task("整理会议议程", "auto"), "general")
        self.assertEqual(classify_task("调研开源项目并比较", "auto"), "research")
        self.assertEqual(classify_task("fix this repo bug and run tests", "auto"), "coding")

    def test_generates_three_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = build_result(self.make_args("根据 PRD 搭建 Codex plugin MVP", tmp))
            files = write_outputs(result, Path(tmp))
            self.assertTrue(files["spec"].exists())
            self.assertTrue(files["agents"].exists())
            self.assertTrue(files["prompt"].exists())
            self.assertEqual(files["spec"].name, "PRE-VIBE-SPEC.MD")
            self.assertEqual(files["agents"].name, "INIT-AGENTS.MD")
            self.assertEqual(files["prompt"].name, "FIRST-PROMPT.MD")
            self.assertIn("PRE-VIBE-SPEC", files["spec"].read_text(encoding="utf-8"))
            self.assertIn("INIT-AGENTS", files["agents"].read_text(encoding="utf-8"))
            prompt = files["prompt"].read_text(encoding="utf-8")
            self.assertIn("FIRST-PROMPT", prompt.upper())
            self.assertLessEqual(result.brief_token_estimate, result.budget.max_injection_tokens)

    def test_skips_secret_like_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, ".env").write_text("TOKEN=secret", encoding="utf-8")
            Path(tmp, "README.md").write_text("# Demo", encoding="utf-8")
            result = build_result(self.make_args("fix code", tmp))
            self.assertIn(".env", result.project_context.skipped_secret_like)
            self.assertIn("README.md", result.project_context.scanned_files)

    def test_micro_mode_skips_project_scan(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "README.md").write_text("# Demo", encoding="utf-8")
            args = self.make_args("整理会议议程", tmp, scenario="general")
            args.mode = "micro"
            result = build_result(args)
            self.assertEqual(result.project_context.scanned_files, [])
            self.assertEqual(result.blocking_questions, [])

    def test_desktop_reverse_request_requires_target_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = build_result(self.make_args("我要逆向一个桌面上的这个东西，我要用上pre-vibe", tmp))
            self.assertEqual(result.scenario, "coding")
            self.assertEqual(result.complexity, "standard")
            self.assertEqual(result.project_context.scanned_files, [])
            self.assertIn("绝对路径", result.blocking_questions[0])
            self.assertIn("不要绕过 DRM", "\n".join(result.hard_constraints))
            files = write_outputs(result, Path(tmp))
            spec = files["spec"].read_text(encoding="utf-8")
            prompt = files["prompt"].read_text(encoding="utf-8")
            self.assertIn("桌面目标对象", prompt)
            self.assertIn("绝对路径", prompt)
            self.assertIn("上下文获取动作", spec)
            self.assertIn("Codex 推荐工作流与设置", spec)
            self.assertIn(".codex/config.toml", spec)
            self.assertIn("用户查看并按需修改", prompt)

    def test_init_agents_reads_global_agents_without_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            codex_home = Path(tmp, "codex-home")
            codex_home.mkdir()
            Path(codex_home, "AGENTS.md").write_text("Never read .env files.\nPrefer short plans.", encoding="utf-8")
            old = os.environ.get("CODEX_HOME")
            os.environ["CODEX_HOME"] = str(codex_home)
            try:
                result = build_result(self.make_args("fix code", tmp))
                files = write_outputs(result, Path(tmp))
                agents = files["agents"].read_text(encoding="utf-8")
                self.assertIn("Never read .env files.", agents)
                self.assertIn("Conflict Policy", agents)
            finally:
                if old is None:
                    os.environ.pop("CODEX_HOME", None)
                else:
                    os.environ["CODEX_HOME"] = old


if __name__ == "__main__":
    unittest.main()
