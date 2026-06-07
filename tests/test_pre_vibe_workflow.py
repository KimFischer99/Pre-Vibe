"""Comprehensive tests for Pre-Vibe plugin workflow modules."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "pre-vibe" / "scripts"
sys.path.insert(0, str(SCRIPTS))

# — routing / classification ——————————————————————————————————————————
from pv_routing import (  # noqa: E402
    assess_risk,
    assess_uncertainty,
    blocking_questions_for,
    can_compile_artifacts,
    choose_intensity,
    choose_language,
    classify_scenario,
    context_actions_for,
    extract_target_paths,
    has_ambiguous_external_target,
    has_cjk,
    has_target_path,
    is_reverse_engineering_task,
    looks_like_new_product_task,
    prepare_project_start,
    route_intake,
)
from pv_models import (  # noqa: E402
    NEEDS_CONTEXT,
    NEEDS_USER_INPUT,
    READY_TO_COMPILE,
    AWAITING_APPROVAL,
    BlockingQuestion,
    IntakeDecision,
    ProjectContext,
)
from pv_questions import (  # noqa: E402
    clean_header,
    native_question_payload,
    option_objects,
    visible_status_for_state,
)
from pv_scan import (  # noqa: E402
    detect_existing_context,
    is_secret_like,
    safe_walk,
)
from pv_artifacts import (  # noqa: E402
    validate_artifact_contents,
    write_artifacts,
    redact_secret_like,
    estimate_tokens,
)
from pv_settings import (  # noqa: E402
    coerce_intensity,
    get_pre_vibe_settings,
    load_pre_vibe_settings,
    resolve_requested_intensity,
    set_pre_vibe_intensity,
    update_pre_vibe_settings,
)
from pv_models import (  # noqa: E402
    INTENSITY_PROFILES,
    PreVibeSettings,
    to_jsonable,
)
from mcp_server import call_tool  # noqa: E402


# ══════════════════════════════════════════════════════════════════════════
#  Language / scenario helpers
# ══════════════════════════════════════════════════════════════════════════

class LanguageDetectionTests(unittest.TestCase):
    def test_has_cjk_detects_chinese(self) -> None:
        self.assertTrue(has_cjk("帮我把这个项目整理好"))
        self.assertTrue(has_cjk("你好世界"))

    def test_has_cjk_rejects_english(self) -> None:
        self.assertFalse(has_cjk("build a small notes app"))
        self.assertFalse(has_cjk(""))

    def test_choose_language_auto_cjk(self) -> None:
        self.assertEqual(choose_language("帮我写代码"), "zh")
        self.assertEqual(choose_language("build an app"), "en")

    def test_choose_language_explicit(self) -> None:
        self.assertEqual(choose_language("anything", "zh"), "zh")
        self.assertEqual(choose_language("anything", "en"), "en")
        self.assertEqual(choose_language("anything", "bilingual"), "bilingual")


class ScenarioClassificationTests(unittest.TestCase):
    def test_classify_coding(self) -> None:
        self.assertEqual(classify_scenario("fix bug in repo"), "coding")
        self.assertEqual(classify_scenario("deploy the api"), "coding")
        self.assertEqual(classify_scenario("写一个前端插件"), "coding")

    def test_classify_research(self) -> None:
        self.assertEqual(classify_scenario("research market options"), "research")
        self.assertEqual(classify_scenario("compare three libraries"), "research")
        self.assertEqual(classify_scenario("调研竞品"), "research")

    def test_classify_mixed(self) -> None:
        self.assertEqual(classify_scenario("research and fix the code"), "mixed")
        self.assertEqual(classify_scenario("compare apis and deploy"), "mixed")

    def test_classify_general(self) -> None:
        self.assertEqual(classify_scenario("hello world"), "general")
        self.assertEqual(classify_scenario("help me understand something"), "general")

    def test_classify_explicit(self) -> None:
        self.assertEqual(classify_scenario("anything", "coding"), "coding")
        self.assertEqual(classify_scenario("anything", "research"), "research")


class IntensitySelectionTests(unittest.TestCase):
    def test_explicit_intensity(self) -> None:
        self.assertEqual(choose_intensity("task", "coding", "mini"), "mini")
        self.assertEqual(choose_intensity("task", "coding", "architect"), "architect")

    def test_explicit_invalid_raises(self) -> None:
        with self.assertRaises(ValueError):
            choose_intensity("task", "coding", "superpower")

    def test_auto_general_defaults_mini(self) -> None:
        self.assertEqual(choose_intensity("help me", "general"), "mini")

    def test_auto_architect_terms(self) -> None:
        self.assertEqual(choose_intensity("refactor the architecture", "coding"), "architect")
        self.assertEqual(choose_intensity("system design for new project", "coding"), "architect")

    def test_auto_default(self) -> None:
        self.assertEqual(choose_intensity("fix a small bug", "coding"), "default")
        self.assertEqual(choose_intensity("compare two papers", "research"), "default")


# ══════════════════════════════════════════════════════════════════════════
#  Target / reverse-engineering detection
# ══════════════════════════════════════════════════════════════════════════

class TargetDetectionTests(unittest.TestCase):
    def test_extract_target_paths_unix(self) -> None:
        paths = extract_target_paths("look at /home/user/app.exe")
        self.assertIn("/home/user/app.exe", paths)

    def test_extract_target_paths_backtick(self) -> None:
        paths = extract_target_paths("analyze `/usr/bin/tool` for me")
        self.assertIn("/usr/bin/tool", paths)

    def test_extract_target_paths_none(self) -> None:
        paths = extract_target_paths("build a new web app")
        self.assertEqual(paths, [])

    def test_has_target_path(self) -> None:
        self.assertTrue(has_target_path("check /path/to/file.dll"))
        self.assertFalse(has_target_path("write some code"))

    def test_has_ambiguous_external_target(self) -> None:
        self.assertTrue(has_ambiguous_external_target("reverse this thing on my desktop"))
        self.assertFalse(has_ambiguous_external_target("reverse /specific/file.exe"))

    def test_is_reverse_engineering_task(self) -> None:
        self.assertTrue(is_reverse_engineering_task("decompile this binary"))
        self.assertTrue(is_reverse_engineering_task("reverse engineer the app"))
        self.assertFalse(is_reverse_engineering_task("build a plugin"))

    def test_looks_like_new_product_task(self) -> None:
        self.assertTrue(looks_like_new_product_task("create a new website for users"))
        self.assertTrue(looks_like_new_product_task("build an mvp app"))
        self.assertFalse(looks_like_new_product_task("fix the login bug"))


# ══════════════════════════════════════════════════════════════════════════
#  Risk / uncertainty assessment
# ══════════════════════════════════════════════════════════════════════════

class RiskAssessmentTests(unittest.TestCase):
    def test_high_risk_deploy(self) -> None:
        self.assertEqual(assess_risk("deploy to production", "coding"), "high")

    def test_high_risk_migration(self) -> None:
        self.assertEqual(assess_risk("run a database migration", "coding"), "high")

    def test_high_risk_reverse(self) -> None:
        self.assertEqual(assess_risk("reverse engineer this thing", "general"), "high")

    def test_medium_risk(self) -> None:
        self.assertEqual(assess_risk("add a new endpoint", "coding"), "medium")

    def test_low_risk(self) -> None:
        self.assertEqual(assess_risk("rename a variable", "general"), "low")


class UncertaintyAssessmentTests(unittest.TestCase):
    def test_high_uncertainty_vague(self) -> None:
        self.assertEqual(assess_uncertainty("make it better"), "high")
        self.assertEqual(assess_uncertainty("搞一下"), "high")

    def test_high_uncertainty_ambiguous_target(self) -> None:
        self.assertEqual(assess_uncertainty("reverse this thing on my desktop"), "high")

    def test_medium_uncertainty_short(self) -> None:
        self.assertEqual(assess_uncertainty("fix bug"), "medium")

    def test_low_uncertainty_detailed(self) -> None:
        task = "Add a logout button to the top-right navigation bar that calls the /api/logout endpoint"
        self.assertEqual(assess_uncertainty(task), "low")


# ══════════════════════════════════════════════════════════════════════════
#  Blocking questions
# ══════════════════════════════════════════════════════════════════════════

class BlockingQuestionsTests(unittest.TestCase):
    def test_questions_for_ambiguous_reverse(self) -> None:
        qs = blocking_questions_for("reverse this thing on my desktop", "general", "default", "en")
        self.assertTrue(any("target" in q.id for q in qs))

    def test_questions_for_new_product(self) -> None:
        qs = blocking_questions_for("build a new website", "coding", "default", "en")
        ids = {q.id for q in qs}
        self.assertIn("core_user_flow", ids)
        self.assertIn("delivery_boundary", ids)

    def test_questions_for_research(self) -> None:
        qs = blocking_questions_for("research the best framework", "research", "default", "en")
        self.assertTrue(any("research_decision" in q.id for q in qs))

    def test_questions_for_deploy(self) -> None:
        qs = blocking_questions_for("deploy the app", "coding", "default", "en")
        self.assertTrue(any("deployment" in q.id for q in qs))

    def test_questions_respect_max(self) -> None:
        qs = blocking_questions_for("build a new app with deploy and auth", "coding", "mini", "en")
        self.assertLessEqual(len(qs), INTENSITY_PROFILES["mini"].max_questions)

    def test_questions_chinese(self) -> None:
        qs = blocking_questions_for("搭建一个新网站", "coding", "default", "zh")
        self.assertTrue(len(qs) > 0)
        # questions should have Chinese content
        self.assertTrue(any("核心流程" in q.header for q in qs))


# ══════════════════════════════════════════════════════════════════════════
#  Context actions
# ══════════════════════════════════════════════════════════════════════════

class ContextActionsTests(unittest.TestCase):
    def test_actions_without_scan(self) -> None:
        actions = context_actions_for("build app", "coding", "default")
        self.assertTrue(any(a.id == "project_execution_index" for a in actions))

    def test_actions_with_scan(self) -> None:
        ctx = ProjectContext(
            ".", True, "scanned", ["README.md"], [], ["src"], {}, [], [],
            None, [], None, [], [], None, "clean",
        )
        actions = context_actions_for("build app", "coding", "default", project_context=ctx)
        self.assertFalse(any(a.id == "project_execution_index" and a.required for a in actions))

    def test_actions_research_allows_fetch(self) -> None:
        actions = context_actions_for("research market", "research", "default")
        self.assertTrue(any(a.kind == "fetch_plan" for a in actions))

    def test_actions_mini_no_fetch(self) -> None:
        actions = context_actions_for("research market", "research", "mini")
        self.assertFalse(any(a.kind == "fetch_plan" for a in actions))


# ══════════════════════════════════════════════════════════════════════════
#  Question UI helpers
# ══════════════════════════════════════════════════════════════════════════

class QuestionUITests(unittest.TestCase):
    def test_clean_header_trims_whitespace(self) -> None:
        self.assertEqual(clean_header("  Hello World  "), "Hello World")

    def test_clean_header_max_length(self) -> None:
        header = clean_header("a" * 50)
        self.assertLessEqual(len(header), 12)

    def test_option_objects_returns_list(self) -> None:
        q = BlockingQuestion("q1", "Test", "What?", "Reason", ["A", "B"], "A")
        opts = option_objects(q)
        self.assertGreaterEqual(len(opts), 1)
        # recommended answer should come first
        self.assertIn("Recommended", opts[0]["label"])

    def test_native_question_payload_empty(self) -> None:
        decision = IntakeDecision(
            raw_input="test", scenario="general", intensity="mini",
            language="en", risk="low", uncertainty="low",
            state=READY_TO_COMPILE,
            blocking_questions=[], context_actions=[], assumptions=[],
            artifact_rules=[], evidence_refs=[],
        )
        self.assertIsNone(native_question_payload(decision))

    def test_native_question_payload_with_questions(self) -> None:
        q = BlockingQuestion("test_q", "Header", "Question text?", "Reason", ["A", "B"], "A")
        decision = IntakeDecision(
            raw_input="test", scenario="general", intensity="default",
            language="en", risk="low", uncertainty="low",
            state=NEEDS_USER_INPUT,
            blocking_questions=[q], context_actions=[], assumptions=[],
            artifact_rules=[], evidence_refs=[],
        )
        payload = native_question_payload(decision)
        self.assertIsNotNone(payload)
        self.assertIn("mcp_elicitation", payload)
        self.assertIn("test_q", payload["mcp_elicitation"]["requestedSchema"]["required"])

    def test_visible_status_for_state(self) -> None:
        self.assertIn("Reading", visible_status_for_state(NEEDS_CONTEXT, "en"))
        self.assertIn("Opening", visible_status_for_state(NEEDS_USER_INPUT, "en"))
        self.assertIn("Building", visible_status_for_state(READY_TO_COMPILE, "en"))
        self.assertIn("ready", visible_status_for_state(AWAITING_APPROVAL, "en"))
        self.assertIn("正在", visible_status_for_state(NEEDS_CONTEXT, "zh"))


# ══════════════════════════════════════════════════════════════════════════
#  Project scanning
# ══════════════════════════════════════════════════════════════════════════

class SecretDetectionTests(unittest.TestCase):
    def test_is_secret_like_env(self) -> None:
        self.assertTrue(is_secret_like(Path(".env")))
        self.assertTrue(is_secret_like(Path("some/path/.env.production")))

    def test_is_secret_like_key(self) -> None:
        self.assertTrue(is_secret_like(Path("id_rsa")))
        self.assertTrue(is_secret_like(Path("server.pem")))

    def test_is_secret_like_token(self) -> None:
        self.assertTrue(is_secret_like(Path("api_token.conf")))
        self.assertTrue(is_secret_like(Path("credentials.json")))

    def test_is_not_secret(self) -> None:
        self.assertFalse(is_secret_like(Path("README.md")))
        self.assertFalse(is_secret_like(Path("main.py")))


class SafeWalkTests(unittest.TestCase):
    def test_walk_missing_root(self) -> None:
        ctx = safe_walk(Path("/nonexistent/path"), 10, "coding")
        self.assertFalse(ctx.scan_performed)
        self.assertIn("missing", ctx.scan_scope)

    def test_walk_zero_max_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ctx = safe_walk(Path(tmp), 0, "coding")
            self.assertFalse(ctx.scan_performed)
            self.assertEqual(ctx.scan_scope, "scan skipped by intensity profile")

    def test_walk_scans_allowlisted_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "README.md").write_text("# hello", encoding="utf-8")
            (Path(tmp) / "package.json").write_text("{}", encoding="utf-8")
            (Path(tmp) / "secret.env").write_text("TOKEN=abc", encoding="utf-8")
            ctx = safe_walk(Path(tmp), 20, "coding")
            self.assertTrue(ctx.scan_performed)
            self.assertIn("README.md", ctx.scanned_files)
            self.assertIn("package.json", ctx.scanned_files)
            self.assertIn("secret.env", ctx.skipped_secret_like)

    def test_walk_detects_git(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".git").mkdir()
            ctx = safe_walk(Path(tmp), 10, "coding")
            self.assertIn(ctx.git_state, {"clean", "dirty", "unknown"})

    def test_walk_skips_hidden_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "node_modules").mkdir()
            (Path(tmp) / "__pycache__").mkdir()
            ctx = safe_walk(Path(tmp), 10, "coding")
            self.assertIn("node_modules/", ctx.do_not_touch)
            self.assertIn("__pycache__/", ctx.do_not_touch)

    def test_walk_signals_stack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "package.json").write_text("{}", encoding="utf-8")
            ctx = safe_walk(Path(tmp), 10, "coding")
            self.assertIn("stack", ctx.signals)
            self.assertEqual(ctx.signals["stack"], "JavaScript/TypeScript")

    def test_walk_signals_python(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "pyproject.toml").write_text("", encoding="utf-8")
            ctx = safe_walk(Path(tmp), 10, "coding")
            self.assertIn("stack", ctx.signals)
            self.assertEqual(ctx.signals["stack"], "Python")


class ExistingContextTests(unittest.TestCase):
    def test_no_existing_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ctx = detect_existing_context(Path(tmp))
            self.assertEqual(ctx.recommended_action, "create_new_context")
            self.assertFalse(ctx.has_pre_vibe_docs)

    def test_full_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "PRE_VIBE_SPEC.md").touch()
            (Path(tmp) / "FIRST_PROMPT.md").touch()
            (Path(tmp) / "CLAUDE.md").touch()
            ctx = detect_existing_context(Path(tmp))
            self.assertTrue(ctx.has_pre_vibe_docs)
            self.assertEqual(ctx.recommended_action, "reuse_update_or_compare")

    def test_partial_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "PRE_VIBE_SPEC.md").touch()
            # missing FIRST_PROMPT.md and CLAUDE.md
            ctx = detect_existing_context(Path(tmp))
            self.assertTrue(ctx.has_partial_pre_vibe_docs)
            self.assertEqual(ctx.recommended_action, "complete_missing_context")


# ══════════════════════════════════════════════════════════════════════════
#  Artifact validation
# ══════════════════════════════════════════════════════════════════════════

class ArtifactValidationTests(unittest.TestCase):
    def test_requires_spec_and_prompt(self) -> None:
        with self.assertRaises(ValueError):
            validate_artifact_contents({"agents": "# Agents"}, allow_project_index=False)

    def test_requires_agents_or_project_agents(self) -> None:
        with self.assertRaises(ValueError):
            validate_artifact_contents(
                {"spec": "# S", "prompt": "# P"}, allow_project_index=False,
            )

    def test_project_index_only_for_architect(self) -> None:
        with self.assertRaises(ValueError):
            validate_artifact_contents(
                {"spec": "# S", "agents": "# A", "prompt": "# P", "project_index": "# I"},
                allow_project_index=False,
            )

    def test_rejects_cross_references(self) -> None:
        with self.assertRaises(ValueError):
            validate_artifact_contents(
                {"spec": "See CLAUDE.md for details", "agents": "# A", "prompt": "# P"},
                allow_project_index=False,
            )

    def test_rejects_both_agents_and_project_agents(self) -> None:
        with self.assertRaises(ValueError):
            validate_artifact_contents(
                {
                    "spec": "# S",
                    "agents": "# A",
                    "project_agents": "# PA",
                    "prompt": "# P",
                },
                allow_project_index=False,
            )

    def test_accepts_valid_contents(self) -> None:
        validate_artifact_contents(
            {"spec": "# Spec", "agents": "# Agents", "prompt": "# Prompt"},
            allow_project_index=False,
        )

    def test_accepts_project_agents(self) -> None:
        validate_artifact_contents(
            {"spec": "# Spec", "project_agents": "# Project Agents", "prompt": "# Prompt"},
            allow_project_index=False,
        )

    def test_accepts_project_index_for_architect(self) -> None:
        validate_artifact_contents(
            {
                "spec": "# S",
                "agents": "# A",
                "prompt": "# P",
                "project_index": "# I",
            },
            allow_project_index=True,
        )


class ArtifactWriteTests(unittest.TestCase):
    def test_write_artifacts_creates_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = write_artifacts(
                Path(tmp),
                {
                    "spec": "# Project Spec\n\nA test handbook.",
                    "agents": "# Agents\n\nExecution rules for the project.",
                    "prompt": "# First Prompt\n\nContinue from here.",
                },
                project_root=Path(tmp),
                allow_project_index=False,
            )
            self.assertIn("spec", result["written"])
            self.assertTrue((Path(tmp) / "PRE_VIBE_SPEC.md").exists())
            self.assertTrue((Path(tmp) / "CLAUDE.md").exists())
            self.assertTrue((Path(tmp) / "FIRST_PROMPT.md").exists())

    def test_write_artifacts_rejects_status_param(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                write_artifacts(
                    Path(tmp),
                    {"spec": "# S", "agents": "# A", "prompt": "# P"},
                    status={"internal": True},
                    project_root=Path(tmp),
                    allow_project_index=False,
                )

    def test_write_artifacts_handoff_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = write_artifacts(
                Path(tmp),
                {"spec": "# S", "agents": "# A", "prompt": "# P"},
                project_root=Path(tmp),
                allow_project_index=False,
            )
            self.assertEqual(result["handoff"]["workflow_state"], AWAITING_APPROVAL)
            self.assertFalse(result["handoff"]["pre_vibe_run_is_complete"])
            self.assertIn("required_next_actions", result["handoff"])


class RedactionTests(unittest.TestCase):
    def test_redact_api_key(self) -> None:
        text = "api_key: sk-abc123def456"
        result = redact_secret_like(text)
        self.assertNotIn("sk-abc123def456", result)

    def test_redact_bearer_token(self) -> None:
        text = "Authorization: bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0"
        result = redact_secret_like(text)
        self.assertNotIn("eyJhbGci", result)

    def test_redact_private_key(self) -> None:
        text = "-----BEGIN RSA PRIVATE KEY-----\nABCDEF123456\n-----END RSA PRIVATE KEY-----"
        result = redact_secret_like(text)
        self.assertNotIn("ABCDEF123456", result)

    def test_non_secret_unchanged(self) -> None:
        text = "This is a normal description."
        result = redact_secret_like(text)
        self.assertEqual(result, text)


class TokenEstimationTests(unittest.TestCase):
    def test_estimate_english(self) -> None:
        tokens = estimate_tokens("hello world")
        self.assertGreater(tokens, 0)

    def test_estimate_cjk(self) -> None:
        tokens = estimate_tokens("你好世界")
        self.assertGreater(tokens, 0)

    def test_estimate_empty(self) -> None:
        tokens = estimate_tokens("")
        self.assertEqual(tokens, 1)


# ══════════════════════════════════════════════════════════════════════════
#  Settings
# ══════════════════════════════════════════════════════════════════════════

class SettingsTests(unittest.TestCase):
    def test_coerce_intensity_valid(self) -> None:
        self.assertEqual(coerce_intensity("mini"), "mini")
        self.assertEqual(coerce_intensity("architect"), "architect")
        self.assertEqual(coerce_intensity(None), "auto")
        self.assertEqual(coerce_intensity(""), "auto")

    def test_coerce_intensity_invalid(self) -> None:
        with self.assertRaises(ValueError):
            coerce_intensity("superpower")

    def test_load_defaults_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            settings = load_pre_vibe_settings(Path(tmp))
            self.assertEqual(settings.default_intensity, "auto")
            self.assertTrue(settings.allow_auto_upgrade)
            self.assertTrue(settings.architect_project_index)
            self.assertTrue(settings.inspect_codex_environment)

    def test_save_and_load_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            update_pre_vibe_settings(
                Path(tmp),
                default_intensity="architect",
                allow_auto_upgrade=False,
                architect_project_index=False,
                inspect_codex_environment=False,
            )
            loaded = load_pre_vibe_settings(Path(tmp))
            self.assertEqual(loaded.default_intensity, "architect")
            self.assertFalse(loaded.allow_auto_upgrade)
            self.assertFalse(loaded.architect_project_index)
            self.assertFalse(loaded.inspect_codex_environment)

    def test_get_settings_returns_dict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = get_pre_vibe_settings(Path(tmp))
            self.assertIsInstance(result, dict)
            self.assertIn("default_intensity", result)

    def test_resolve_explicit_overrides_settings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            update_pre_vibe_settings(Path(tmp), default_intensity="mini")
            intensity, _ = resolve_requested_intensity(Path(tmp), "architect")
            self.assertEqual(intensity, "architect")

    def test_resolve_falls_back_to_settings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            update_pre_vibe_settings(Path(tmp), default_intensity="architect")
            intensity, _ = resolve_requested_intensity(Path(tmp))
            self.assertEqual(intensity, "architect")

    def test_resolve_returns_auto_when_nothing_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            intensity, _ = resolve_requested_intensity(Path(tmp))
            self.assertEqual(intensity, "auto")

    def test_set_session_intensity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = set_pre_vibe_intensity(Path(tmp), "architect")
            self.assertEqual(result["session_intensity"], "architect")

    def test_set_session_intensity_auto_clears(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            set_pre_vibe_intensity(Path(tmp), "architect")
            result = set_pre_vibe_intensity(Path(tmp), "auto")
            self.assertEqual(result["session_intensity"], "auto")


class SettingsBadFileTests(unittest.TestCase):
    def test_corrupted_settings_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            settings_dir = Path(tmp) / ".pre-vibe"
            settings_dir.mkdir()
            (settings_dir / "settings.json").write_text("not valid json", encoding="utf-8")
            settings = load_pre_vibe_settings(Path(tmp))
            self.assertEqual(settings.default_intensity, "auto")

    def test_settings_not_a_dict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            settings_dir = Path(tmp) / ".pre-vibe"
            settings_dir.mkdir()
            (settings_dir / "settings.json").write_text("[]", encoding="utf-8")
            settings = load_pre_vibe_settings(Path(tmp))
            self.assertEqual(settings.default_intensity, "auto")


# ══════════════════════════════════════════════════════════════════════════
#  Models / serialization
# ══════════════════════════════════════════════════════════════════════════

class ModelSerializationTests(unittest.TestCase):
    def test_to_jsonable_dataclass(self) -> None:
        result = to_jsonable(PreVibeSettings(default_intensity="mini"))
        self.assertIsInstance(result, dict)
        self.assertEqual(result["default_intensity"], "mini")

    def test_to_jsonable_path(self) -> None:
        result = to_jsonable(Path("/some/path"))
        self.assertEqual(result, "/some/path")

    def test_to_jsonable_non_dataclass_raises(self) -> None:
        with self.assertRaises(TypeError):
            to_jsonable(object())


# ══════════════════════════════════════════════════════════════════════════
#  Route intake (end-to-end routing)
# ══════════════════════════════════════════════════════════════════════════

class RouteIntakeTests(unittest.TestCase):
    def test_route_intake_coding_task(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            decision = route_intake("fix the login bug", tmp, scan=False, intensity="mini")
            self.assertIsInstance(decision, IntakeDecision)
            self.assertEqual(decision.scenario, "coding")
            self.assertEqual(decision.intensity, "mini")

    def test_route_intake_research_task(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            decision = route_intake("research the best database", tmp, scan=False, intensity="mini")
            self.assertEqual(decision.scenario, "research")

    def test_route_intake_general_task(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            decision = route_intake("hello", tmp, scan=False, intensity="mini")
            self.assertEqual(decision.scenario, "general")

    def test_route_intake_can_compile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            decision = route_intake("fix a bug", tmp, scan=True, intensity="mini")
            self.assertTrue(can_compile_artifacts(decision))


# ══════════════════════════════════════════════════════════════════════════
#  MCP server tool dispatch
# ══════════════════════════════════════════════════════════════════════════

class MCPServerDispatchTests(unittest.TestCase):
    def test_call_unknown_tool_raises(self) -> None:
        with self.assertRaises(ValueError):
            call_tool("nonexistent_tool", {})

    def test_call_prepare_project_start(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = call_tool("prepare_project_start", {
                "task": "Build a notes app",
                "project": tmp,
                "scan": False,
                "intensity": "mini",
            })
            self.assertIn("content", result)
            self.assertIn("structuredContent", result)
            sc = result["structuredContent"]
            self.assertIn("state", sc)
            self.assertIn("workflow_contract", sc)

    def test_call_get_pre_vibe_settings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = call_tool("get_pre_vibe_settings", {"project": tmp})
            self.assertIn("structuredContent", result)
            self.assertIn("default_intensity", result["structuredContent"])

    def test_call_update_pre_vibe_settings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = call_tool("update_pre_vibe_settings", {
                "project": tmp,
                "default_intensity": "architect",
            })
            sc = result["structuredContent"]
            self.assertEqual(sc["settings"]["default_intensity"], "architect")

    def test_call_set_pre_vibe_intensity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = call_tool("set_pre_vibe_intensity", {
                "project": tmp,
                "intensity": "mini",
            })
            sc = result["structuredContent"]
            self.assertEqual(sc["session_intensity"], "mini")

    def test_call_scan_project_safe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = call_tool("scan_project_safe", {"project": tmp, "intensity": "mini"})
            sc = result["structuredContent"]
            self.assertIn("scan_scope", sc)

    def test_call_write_project_starting_documents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = call_tool("write_project_starting_documents", {
                "output_dir": tmp,
                "project_root": tmp,
                "contents": {
                    "spec": "# Spec",
                    "agents": "# Agents",
                    "prompt": "# Prompt",
                },
                "intensity": "default",
            })
            sc = result["structuredContent"]
            self.assertIn("handoff", sc)
            self.assertEqual(sc["handoff"]["workflow_state"], AWAITING_APPROVAL)


# ══════════════════════════════════════════════════════════════════════════
#  Workflow contract integration tests (original tests preserved)
# ══════════════════════════════════════════════════════════════════════════

class PreVibeWorkflowTests(unittest.TestCase):
    def test_prepare_project_start_returns_handoff_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            payload = prepare_project_start(
                "Build a small local notes app",
                tmp,
                scan=False,
                intensity="mini",
            )

        contract = payload["workflow_contract"]
        self.assertTrue(contract["document_generation_is_not_completion"])
        self.assertTrue(
            any("write_project_starting_documents" in step for step in contract["required_order"])
        )
        self.assertIn("explicit user approval", contract["required_order"][-1])

    def test_write_artifacts_requires_approval_before_completion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = write_artifacts(
                Path(tmp),
                {
                    "spec": "# Spec\n\nProject handbook.",
                    "agents": "# Agents\n\nExecution rules.",
                    "prompt": "# First Prompt\n\nContinue from this contract.",
                },
                project_root=Path(tmp),
                allow_project_index=False,
            )

        self.assertEqual(result["written"]["prompt"], "FIRST_PROMPT.md")
        self.assertEqual(result["handoff"]["workflow_state"], AWAITING_APPROVAL)
        self.assertFalse(result["handoff"]["pre_vibe_run_is_complete"])
        self.assertIn("Present FIRST_PROMPT", result["handoff"]["required_next_actions"][0])

    def test_default_effort_rejects_project_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                write_artifacts(
                    Path(tmp),
                    {
                        "spec": "# Spec",
                        "agents": "# Agents",
                        "prompt": "# First Prompt",
                        "project_index": "# Index",
                    },
                    project_root=Path(tmp),
                    allow_project_index=False,
                )

    def test_can_disable_claude_code_environment_inspection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            update_pre_vibe_settings(Path(tmp), inspect_codex_environment=False)
            payload = prepare_project_start(
                "Prepare this repo for a small coding task",
                tmp,
                scan=False,
                intensity="mini",
            )

            tool_result = call_tool("inspect_codex_environment", {"project": tmp})

        self.assertIsNone(payload["codex_environment"])
        self.assertEqual(payload["component_suggestions"], [])
        self.assertEqual(payload["missing_component_suggestions"], [])
        self.assertFalse(
            any(ref["id"] == "codex_component_index" for ref in payload["evidence_refs"])
        )
        self.assertFalse(tool_result["structuredContent"]["inspection_enabled"])


if __name__ == "__main__":
    unittest.main()
