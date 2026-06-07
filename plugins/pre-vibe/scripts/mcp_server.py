#!/usr/bin/env python3
"""Minimal MCP stdio server for pre-vibe workflow helpers."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from pre_vibe import (
    get_pre_vibe_settings,
    inspect_codex_environment,
    prepare_project_start,
    safe_walk,
    set_pre_vibe_intensity,
    to_jsonable,
    update_pre_vibe_settings,
    write_artifacts,
    INTENSITY_PROFILES,
)


SERVER_INSTRUCTIONS = (
    "Pre-Vibe prepares project starting context before implementation. "
    "Show only short user-facing status text in chat; keep structured workflow fields in structuredContent. "
    "When structuredContent.question_request is present, Claude Code opens native question UI automatically. "
    "Write PRE_VIBE_SPEC.md, CLAUDE.md or PROJECT_CLAUDE.md, and FIRST_PROMPT.md; architect effort may also write PROJECT_INDEX.md. "
    "Do not write internal intake/status/context fields to disk, and keep output paths inside the active project. "
    "Writing documents is not the end of the workflow: after write_project_starting_documents, request user approval for FIRST_PROMPT.md, then read and inject FIRST_PROMPT.md as the execution contract when approved."
)


def json_safe(payload: Any) -> Any:
    return json.loads(json.dumps(payload, ensure_ascii=False, default=to_jsonable))


def text_result(payload: Any, public_text: str | None = None) -> dict[str, Any]:
    if public_text is None:
        public_text = json.dumps(payload, ensure_ascii=False, indent=2, default=to_jsonable)
        return {
            "content": [
                {
                    "type": "text",
                    "text": public_text,
                }
            ]
        }
    return {
        "content": [
            {
                "type": "text",
                "text": public_text,
            }
        ],
        "structuredContent": json_safe(payload),
    }


def tool_schema() -> list[dict[str, Any]]:
    return [
        {
            "name": "prepare_project_start",
            "description": "First step for Pre-Vibe. Read safe project/Claude Code context, choose effort level, and return the mandatory workflow contract. If structuredContent.question_request is present, call open_question_dialog before writing documents. Do not print structured fields in chat.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task": {"type": "string"},
                    "project": {"type": "string", "default": "."},
                    "scenario": {
                        "type": "string",
                        "enum": ["auto", "general", "research", "coding", "mixed"],
                        "default": "auto",
                    },
                    "intensity": {
                        "type": "string",
                        "enum": ["auto", "mini", "default", "architect"],
                        "default": "auto",
                    },
                    "language": {
                        "type": "string",
                        "enum": ["auto", "zh", "en", "bilingual"],
                        "default": "auto",
                    },
                    "scan": {"type": "boolean", "default": True},
                },
                "required": ["task"],
            },
        },
        {
            "name": "get_pre_vibe_settings",
            "description": "Read project-local Pre-Vibe settings, including default effort level and session override.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project": {"type": "string", "default": "."},
                },
            },
        },
        {
            "name": "set_effort_level",
            "description": "Set Pre-Vibe effort level for this session. Choose the level that fits your task.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "level": {
                        "type": "string",
                        "enum": ["mini", "default", "architect"],
                        "description": "mini → quick tasks: up to 3 questions, minimal preparation. default → normal coding/research: up to 5 questions, balanced depth. architect → complex projects/refactors: up to 10 questions, includes PROJECT_INDEX.md."
                    },
                },
                "required": ["level"],
            },
        },
        {
            "name": "update_pre_vibe_settings",
            "description": "Update project-local Pre-Vibe settings. Use this when the user wants to set default effort behavior.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project": {"type": "string", "default": "."},
                    "default_intensity": {
                        "type": "string",
                        "enum": ["auto", "mini", "default", "architect"],
                    },
                    "allow_auto_upgrade": {"type": "boolean"},
                    "architect_project_index": {"type": "boolean"},
                    "inspect_codex_environment": {"type": "boolean"},
                },
            },
        },
        {
            "name": "set_pre_vibe_intensity",
            "description": "Set the current Pre-Vibe session effort level to auto, mini, default, or architect.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project": {"type": "string", "default": "."},
                    "intensity": {
                        "type": "string",
                        "enum": ["auto", "mini", "default", "architect"],
                    },
                },
                "required": ["intensity"],
            },
        },
        {
            "name": "scan_project_safe",
            "description": "Perform an allowlist project scan without reading secrets.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project": {"type": "string", "default": "."},
                    "scenario": {
                        "type": "string",
                        "enum": ["general", "research", "coding", "mixed"],
                        "default": "coding",
                    },
                    "intensity": {
                        "type": "string",
                        "enum": ["mini", "default", "architect"],
                        "default": "default",
                    },
                },
            },
        },
        {
            "name": "inspect_codex_environment",
            "description": "Inspect Claude Code guidance files, installed standalone skills, plugin cache, enabled plugins, and personal marketplace state.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project": {"type": "string", "default": "."},
                },
            },
        },
        {
            "name": "write_project_starting_documents",
            "description": "Pre-Vibe document write step. Write only Claude Code-authored, task-specific project starting documents after required context and user answers are available. This is not the final workflow step: after the tool returns, request user approval for FIRST_PROMPT.md and inject it after approval. Does not generate prose.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "output_dir": {"type": "string", "default": "."},
                    "project_root": {"type": "string", "default": "."},
                    "contents": {
                        "type": "object",
                        "properties": {
                            "spec": {"type": "string"},
                            "agents": {"type": "string"},
                            "project_agents": {"type": "string"},
                            "prompt": {"type": "string"},
                            "project_index": {"type": "string"},
                        },
                        "additionalProperties": {"type": "string"},
                    },
                    "intensity": {
                        "type": "string",
                        "enum": ["mini", "default", "architect"],
                        "default": "default",
                    },
                },
                "required": ["contents"],
            },
        },
    ]


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "prepare_project_start":
        payload = prepare_project_start(
            arguments["task"],
            arguments.get("project", "."),
            scenario=arguments.get("scenario", "auto"),
            intensity=arguments.get("intensity", "auto"),
            language=arguments.get("language", "auto"),
            scan=bool(arguments.get("scan", True)),
        )
        return text_result(payload, payload["user_visible_status"])
    if name == "get_pre_vibe_settings":
        payload = get_pre_vibe_settings(Path(arguments.get("project", ".")))
        return text_result(payload, "正在读取 Pre-Vibe 设置。")
    if name == "update_pre_vibe_settings":
        payload = update_pre_vibe_settings(
            Path(arguments.get("project", ".")),
            default_intensity=arguments.get("default_intensity"),
            allow_auto_upgrade=arguments.get("allow_auto_upgrade"),
            architect_project_index=arguments.get("architect_project_index"),
            inspect_codex_environment=arguments.get("inspect_codex_environment"),
        )
        return text_result(payload, "Pre-Vibe 设置已更新。")
    if name == "set_pre_vibe_intensity":
        payload = set_pre_vibe_intensity(
            Path(arguments.get("project", ".")),
            arguments["intensity"],
        )
        return text_result(payload, "Pre-Vibe 强度档位已设置。")
    if name == "set_effort_level":
        payload = set_pre_vibe_intensity(
            Path("."),
            arguments["level"],
        )
        return text_result(payload, f"Effort level set to: {arguments['level']}.")
    if name == "scan_project_safe":
        intensity = arguments.get("intensity", "default")
        max_files = INTENSITY_PROFILES[intensity].max_scanned_files
        payload = safe_walk(
            Path(arguments.get("project", ".")).expanduser().resolve(),
            max_files,
            arguments.get("scenario", "coding"),
        )
        return text_result(payload, "正在读取项目结构。")
    if name == "inspect_codex_environment":
        settings = get_pre_vibe_settings(Path(arguments.get("project", ".")))
        if not settings.get("inspect_codex_environment", True):
            return text_result(
                {
                    "inspection_enabled": False,
                    "notes": ["Claude Code environment inspection is disabled for this project."],
                },
                "此项目已关闭 Claude Code 环境读取。",
            )
        return text_result(inspect_codex_environment(), "正在读取 Claude Code 环境。")
    if name == "write_project_starting_documents":
        payload = write_artifacts(
            Path(arguments.get("output_dir", ".")),
            arguments["contents"],
            project_root=Path(arguments.get("project_root", ".")),
            allow_project_index=arguments.get("intensity") == "architect",
        )
        return text_result(payload, "项目初始文档已构建，正在等待交接确认。")
    raise ValueError(f"unknown tool: {name}")


def handle(request: dict[str, Any]) -> dict[str, Any] | None:
    method = request.get("method")
    request_id = request.get("id")
    if method == "notifications/initialized":
        return None
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "pre-vibe", "version": "0.1.2"},
                "instructions": SERVER_INSTRUCTIONS,
            },
        }
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tool_schema()}}
    if method == "tools/call":
        params = request.get("params", {})
        try:
            result = call_tool(params.get("name", ""), params.get("arguments", {}) or {})
            return {"jsonrpc": "2.0", "id": request_id, "result": result}
        except Exception as exc:  # MCP errors should stay JSON-serializable.
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32000, "message": str(exc)},
            }
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": f"unknown method: {method}"},
    }


def main() -> int:
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError as exc:
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"parse error: {exc.msg}"},
            }
        else:
            response = handle(request)
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
