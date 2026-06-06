#!/usr/bin/env python3
"""Minimal MCP stdio server for pre-vibe workflow helpers."""

from __future__ import annotations

import json
import select
import sys
from pathlib import Path
from typing import Any

from pre_vibe import (
    inspect_codex_environment,
    prepare_project_start,
    safe_walk,
    to_jsonable,
    write_artifacts,
    INTENSITY_PROFILES,
)


_CLIENT_REQUEST_ID = 10_000


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
            "description": "First step for Pre-Vibe. Read safe project/Codex context, choose effort level, and return the next workflow action. If structuredContent.question_request is present, call open_question_dialog before writing documents. Do not print structured fields in chat.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task": {"type": "string"},
                    "project": {"type": "string", "default": "."},
                    "scenario": {"type": "string", "default": "auto"},
                    "intensity": {"type": "string", "default": "auto"},
                    "language": {"type": "string", "default": "auto"},
                    "scan": {"type": "boolean", "default": True},
                },
                "required": ["task"],
            },
        },
        {
            "name": "open_question_dialog",
            "description": "Open Codex native MCP elicitation for blocking questions returned by prepare_project_start. Use this instead of printing questions in chat.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "default": "Please answer the key questions so Codex can continue."},
                    "requestedSchema": {"type": "object"},
                    "questions": {
                        "type": "array",
                        "items": {"type": "object"},
                    },
                    "timeout_seconds": {"type": "integer", "default": 900},
                },
            },
        },
        {
            "name": "scan_project_safe",
            "description": "Perform an allowlist project scan without reading secrets.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project": {"type": "string", "default": "."},
                    "scenario": {"type": "string", "default": "coding"},
                    "intensity": {"type": "string", "default": "default"},
                },
            },
        },
        {
            "name": "inspect_codex_environment",
            "description": "Inspect Codex AGENTS, installed standalone skills, plugin cache, enabled plugins, and personal marketplace state.",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "write_project_starting_documents",
            "description": "Final Pre-Vibe write step. Write only Codex-authored, task-specific project starting documents after required context and user answers are available. Does not generate prose.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "output_dir": {"type": "string", "default": "."},
                    "contents": {
                        "type": "object",
                        "additionalProperties": {"type": "string"},
                    },
                    "status": {"type": "object"},
                },
                "required": ["contents"],
            },
        },
    ]


def schema_from_questions(questions: list[dict[str, Any]]) -> dict[str, Any]:
    properties: dict[str, Any] = {}
    required: list[str] = []
    for index, question in enumerate(questions):
        qid = str(question.get("id") or f"question_{index + 1}")
        required.append(qid)
        properties[qid] = {
            "type": "string",
            "title": str(question.get("header") or qid)[:36],
            "description": str(question.get("question") or "Please answer this question."),
        }
    return {"type": "object", "properties": properties, "required": required}


def next_client_request_id() -> int:
    global _CLIENT_REQUEST_ID
    _CLIENT_REQUEST_ID += 1
    return _CLIENT_REQUEST_ID


def request_client_elicitation(arguments: dict[str, Any]) -> dict[str, Any]:
    requested_schema = arguments.get("requestedSchema")
    if not requested_schema and isinstance(arguments.get("questions"), list):
        requested_schema = schema_from_questions(arguments["questions"])
    if not isinstance(requested_schema, dict):
        raise ValueError("open_question_dialog requires requestedSchema or questions")
    request_id = next_client_request_id()
    request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "elicitation/create",
        "params": {
            "message": arguments.get("message") or "Please answer the key questions so Codex can continue.",
            "requestedSchema": requested_schema,
        },
    }
    sys.stdout.write(json.dumps(request, ensure_ascii=False) + "\n")
    sys.stdout.flush()
    timeout = int(arguments.get("timeout_seconds") or 900)
    while True:
        readable, _, _ = select.select([sys.stdin], [], [], max(timeout, 1))
        if not readable:
            return {
                "available": False,
                "reason": "Timed out waiting for Codex native question UI.",
            }
        line = sys.stdin.readline()
        if not line:
            return {
                "available": False,
                "reason": "Codex closed the MCP stream before returning a question UI response.",
            }
        response = json.loads(line)
        if response.get("id") != request_id:
            continue
        if "error" in response:
            return {
                "available": False,
                "reason": "Codex rejected the native question UI request.",
                "error": response["error"],
            }
        return {
            "available": True,
            "response": response.get("result"),
        }


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
    if name == "open_question_dialog":
        payload = request_client_elicitation(arguments)
        public_text = (
            "关键问题已确认，正在构建项目初始文档。"
            if payload.get("available")
            else "当前 Codex 界面未能打开原生提问窗口。"
        )
        return text_result(payload, public_text)
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
        return text_result(inspect_codex_environment(), "正在读取 Codex 环境。")
    if name == "write_project_starting_documents":
        payload = write_artifacts(
            Path(arguments.get("output_dir", ".")),
            arguments["contents"],
            arguments.get("status"),
        )
        return text_result(payload, "项目初始文档已构建。")
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
                "serverInfo": {"name": "pre-vibe", "version": "0.5.0"},
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
        response = handle(json.loads(line))
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
