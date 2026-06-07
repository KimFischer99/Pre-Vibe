from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "pre-vibe" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from pv_artifacts import write_artifacts  # noqa: E402
from pv_models import AWAITING_APPROVAL  # noqa: E402
from pv_routing import prepare_project_start  # noqa: E402
from pv_settings import update_pre_vibe_settings  # noqa: E402
from mcp_server import call_tool  # noqa: E402


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
        self.assertIn("after approval", contract["required_order"][-1])

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
        self.assertIn("Ask the user to approve", result["handoff"]["required_next_actions"][0])

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

    def test_can_disable_codex_environment_inspection(self) -> None:
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
