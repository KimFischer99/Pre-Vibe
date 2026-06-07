"""Claude Code environment inspection helpers."""

from __future__ import annotations

import json
from pathlib import Path

from pv_models import CodexEnvironment
from pv_scan import collect_skill_names, find_global_agents

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback.
    tomllib = None  # type: ignore[assignment]


def collect_configured_plugins(config_path: Path) -> list[str]:
    """Read enabled plugins from Claude Code settings.json."""
    if not config_path.exists():
        return []
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    enabled = payload.get("enabledPlugins", {})
    if not isinstance(enabled, dict):
        return []
    configured: list[str] = []
    for name, value in enabled.items():
        if not isinstance(name, str):
            continue
        if value is True:
            configured.append(name)
    return sorted(configured)


def collect_plugin_names(cache_root: Path, marketplace_path: Path) -> tuple[list[str], list[str], list[str]]:
    cache_entries: list[str] = []
    cached: set[str] = set()
    marketplace_plugins: set[str] = set()
    if cache_root.exists():
        for path in sorted(cache_root.glob("*/*/*")):
            if path.is_dir():
                cache_entries.append(str(path))
                parts = path.relative_to(cache_root).parts
                if len(parts) >= 2:
                    cached.add(f"{parts[1]}@{parts[0]}")
    if marketplace_path.exists():
        try:
            payload = json.loads(marketplace_path.read_text(encoding="utf-8"))
            for item in payload.get("plugins", []):
                if isinstance(item, dict) and isinstance(item.get("name"), str):
                    marketplace_plugins.add(f"{item['name']}@marketplace")
        except json.JSONDecodeError:
            pass
    return cache_entries, sorted(cached), sorted(marketplace_plugins)


def inspect_codex_environment() -> CodexEnvironment:
    claude_home = Path.home() / ".claude"
    global_agents = find_global_agents()
    cache_root = claude_home / "plugins" / "cache"
    marketplace = claude_home / "plugins" / "marketplace.json"
    plugin_cache, cached_plugins, marketplace_plugins = collect_plugin_names(cache_root, marketplace)
    configured_plugins = collect_configured_plugins(claude_home / "settings.json")
    installed_plugins = configured_plugins or cached_plugins
    marketplace_has_pre_vibe = False
    if marketplace.exists():
        try:
            payload = json.loads(marketplace.read_text(encoding="utf-8"))
            marketplace_has_pre_vibe = any(
                isinstance(item, dict) and item.get("name") == "pre-vibe"
                for item in payload.get("plugins", [])
            )
        except json.JSONDecodeError:
            marketplace_has_pre_vibe = False
    skill_roots = [
        claude_home / "skills",
    ]
    notes = []
    if not global_agents:
        notes.append("No global CLAUDE.md was found.")
    if not marketplace_has_pre_vibe:
        notes.append("pre-vibe is not listed in the default personal marketplace.")
    return CodexEnvironment(
        codex_home=str(claude_home),
        global_agents_path=str(global_agents) if global_agents else None,
        installed_plugin_cache=plugin_cache,
        installed_plugins=installed_plugins,
        marketplace_plugins=marketplace_plugins,
        installed_skills=collect_skill_names(skill_roots),
        local_plugins_path=str(claude_home / "plugins"),
        marketplace_path=str(marketplace) if marketplace.exists() else None,
        marketplace_has_pre_vibe=marketplace_has_pre_vibe,
        notes=notes,
    )
