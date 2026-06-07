"""Keyword sets and regular expressions used by Pre-Vibe routing."""

from __future__ import annotations

import re


CODING_TERMS = (
    "code",
    "repo",
    "bug",
    "fix",
    "api",
    "frontend",
    "backend",
    "test",
    "deploy",
    "plugin",
    "mvp",
    "reverse",
    "reverse-engineer",
    "decompile",
    "disassemble",
    "binary analysis",
    "build",
    "create",
    "website",
    "app",
    "页面",
    "网站",
    "应用",
    "小程序",
    "在线",
    "功能",
    "界面",
    "代码",
    "仓库",
    "项目",
    "修复",
    "前端",
    "后端",
    "测试",
    "部署",
    "插件",
    "搭建",
    "营造",
    "构建",
    "开发",
    "编写",
    "实现",
    "逆向",
    "反编译",
    "反汇编",
    "拆包",
)

RESEARCH_TERMS = (
    "research",
    "compare",
    "sources",
    "paper",
    "market",
    "docs",
    "investigate",
    "调研",
    "研究",
    "比较",
    "竞品",
    "资料",
    "论文",
    "文档",
)

REVERSE_TERMS = (
    "reverse",
    "reverse-engineer",
    "decompile",
    "disassemble",
    "binary analysis",
    "逆向",
    "反编译",
    "反汇编",
    "拆包",
)

AMBIGUOUS_TARGET_TERMS = (
    "desktop",
    "on my desktop",
    "this thing",
    "this app",
    "this file",
    "桌面",
    "这个东西",
    "这个应用",
    "这个app",
    "这个文件",
)

ARCHITECT_TERMS = (
    "architecture",
    "architect",
    "system design",
    "refactor",
    "new project",
    "rewrite",
    "workflow",
    "架构",
    "系统设计",
    "重构",
    "新项目",
    "完整",
)

TARGET_PATH_RE = re.compile(
    r"(`[^`]+`|[/~][^\s]+|[A-Za-z]:\\[^\s]+|\b[\w .@()-]+\."
    r"(app|exe|dmg|pkg|zip|asar|apk|ipa|bin|dll|dylib|so|jar|class)\b)",
    re.IGNORECASE,
)
