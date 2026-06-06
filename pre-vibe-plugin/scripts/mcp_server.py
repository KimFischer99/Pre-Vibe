#!/usr/bin/env python3
"""Minimal MCP stdio server for pre-vibe workflow helpers."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from pre_vibe import (
    inspect_codex_environment,
    route_intake,
    safe_walk,
    to_jsonable,
    write_artifacts,
    INTENSITY_PROFILES,
)


def text_result(payload: Any) -> dict[str, Any]:
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(payload, ensure_ascii=False, indent=2, default=to_jsonable),
            }
        ]
    }


def tool_schema() -> list[dict[str, Any]]:
    return [
        {
            "name": "classify_intake",
            "description": "Classify a user request, choose pre-vibe intensity, and return the next workflow state.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task": {"type": "string"},
                    "project": {"type": "string", "default": "."},
                    "scenario": {"type": "string", "default": "auto"},
                    "intensity": {"type": "string", "default": "auto"},
                    "language": {"type": "string", "default": "auto"},
                    "scan": {"type": "boolean", "default": False},
                },
                "required": ["task"],
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
            "description": "Inspect Codex AGENTS, plugin cache, and personal marketplace state.",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "write_pre_vibe_artifacts",
            "description": "Write LLM-authored pre-vibe artifacts and status metadata; does not generate artifact prose.",
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


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "classify_intake":
        return text_result(
            route_intake(
                arguments["task"],
                arguments.get("project", "."),
                scenario=arguments.get("scenario", "auto"),
                intensity=arguments.get("intensity", "auto"),
                language=arguments.get("language", "auto"),
                scan=bool(arguments.get("scan", False)),
            )
        )
    if name == "scan_project_safe":
        intensity = arguments.get("intensity", "default")
        max_files = INTENSITY_PROFILES[intensity].max_scanned_files
        return text_result(
            safe_walk(
                Path(arguments.get("project", ".")).expanduser().resolve(),
                max_files,
                arguments.get("scenario", "coding"),
            )
        )
    if name == "inspect_codex_environment":
        return text_result(inspect_codex_environment())
    if name == "write_pre_vibe_artifacts":
        return text_result(
            write_artifacts(
                Path(arguments.get("output_dir", ".")),
                arguments["contents"],
                arguments.get("status"),
            )
        )
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
                "serverInfo": {"name": "pre-vibe", "version": "0.3.1"},
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
