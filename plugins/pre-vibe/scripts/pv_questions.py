"""Native question UI payloads and user-visible workflow statuses."""

from __future__ import annotations

import re
from typing import Any

from pv_models import (
    AWAITING_APPROVAL,
    DONE,
    NEEDS_CONTEXT,
    NEEDS_USER_INPUT,
    READY_TO_COMPILE,
    READY_TO_INJECT,
    BlockingQuestion,
    IntakeDecision,
)


def clean_header(value: str, fallback: str = "Question") -> str:
    value = re.sub(r"\s+", " ", value).strip() or fallback
    return value[:12]


def option_objects(question: BlockingQuestion) -> list[dict[str, str]]:
    options = list(question.options[:4])
    if len(options) < 2:
        options.extend(["Use best default", "Ask later"][len(options) :])
    if question.recommended_answer and question.recommended_answer in options:
        options = [question.recommended_answer] + [
            option for option in options if option != question.recommended_answer
        ]

    def label_for(option: str) -> str:
        if question.recommended_answer and option == question.recommended_answer:
            suffix = " (Recommended)"
            return f"{option[: 36 - len(suffix)].rstrip()}{suffix}"
        return option[:36]

    def desc_for(option: str, index: int) -> str:
        base = question.reason[:120]
        if question.recommended_answer and option == question.recommended_answer:
            return f"Recommended — {base}"[:160]
        return f"{base}"[:160] or "Choose this option to continue."

    return [
        {
            "label": label_for(option),
            "description": desc_for(option, i),
        }
        for i, option in enumerate(options[:4])
    ]


def native_question_payload(decision: IntakeDecision) -> dict[str, Any] | None:
    if not decision.blocking_questions:
        return None
    questions = [
        {
            "header": clean_header(question.header),
            "id": question.id,
            "question": question.question,
            "recommended_answer": question.recommended_answer,
            "reason": question.reason,
            "options": option_objects(question),
        }
        for question in decision.blocking_questions
    ]
    return {
        "preferred_surface": "claude_code_native_question_ui",
        "codex_request_user_input": {
            "questions": questions,
        },
        "mcp_elicitation": {
            "method": "elicitation/create",
            "message": "Please answer the key questions so Claude Code can build the project starting context.",
            "requestedSchema": {
                "type": "object",
                "properties": {
                    question.id: {
                        "type": "string",
                        "title": clean_header(question.header),
                        "description": question.question,
                    }
                    for question in decision.blocking_questions
                },
                "required": [question.id for question in decision.blocking_questions],
            },
        },
        "fallback_policy": "If this Claude Code surface cannot open native question UI or MCP elicitation, pause and report that native question UI is unavailable instead of printing backend fields.",
    }


def visible_status_for_state(state: str, language: str = "auto") -> str:
    zh = language in {"zh", "bilingual", "auto"}
    if state == NEEDS_CONTEXT:
        return "正在读取项目结构和 Claude Code 环境。" if zh else "Reading the project and Claude Code environment."
    if state == NEEDS_USER_INPUT:
        return "正在打开关键问题确认窗口。" if zh else "Opening the key-question dialog."
    if state == READY_TO_COMPILE:
        return "正在构建项目初始文档。" if zh else "Building the project starting documents."
    if state == AWAITING_APPROVAL:
        return "项目初始文档已准备好，正在等待确认。" if zh else "The project starting documents are ready for approval."
    if state == READY_TO_INJECT:
        return "正在准备清理上下文并注入首轮提示。" if zh else "Preparing to clear context and inject the first prompt."
    if state == DONE:
        return "项目启动上下文已完成。" if zh else "The project starting context is complete."
    return "正在准备项目启动上下文。" if zh else "Preparing the project starting context."
