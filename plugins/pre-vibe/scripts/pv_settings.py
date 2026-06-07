"""Project-local Pre-Vibe settings."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from pv_models import INTENSITY_PROFILES, PreVibeSettings


SETTINGS_PATH = ".pre-vibe/settings.json"
SESSION_SETTINGS: dict[str, PreVibeSettings] = {}
VALID_INTENSITIES = {"auto", *INTENSITY_PROFILES.keys()}


def project_key(project_root: Path) -> str:
    return str(project_root.expanduser().resolve())


def settings_path(project_root: Path) -> Path:
    return project_root.expanduser().resolve() / SETTINGS_PATH


def coerce_intensity(value: str | None, field: str = "intensity") -> str:
    selected = value or "auto"
    if selected not in VALID_INTENSITIES:
        raise ValueError(f"unknown {field}: {selected}")
    return selected


def load_pre_vibe_settings(project_root: Path) -> PreVibeSettings:
    path = settings_path(project_root)
    if not path.exists():
        return PreVibeSettings()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return PreVibeSettings()
    if not isinstance(payload, dict):
        return PreVibeSettings()
    try:
        default_intensity = coerce_intensity(str(payload.get("default_intensity", "auto")), "default_intensity")
    except ValueError:
        default_intensity = "auto"
    return PreVibeSettings(
        default_intensity=default_intensity,
        allow_auto_upgrade=bool(payload.get("allow_auto_upgrade", True)),
        architect_project_index=bool(payload.get("architect_project_index", True)),
        inspect_codex_environment=bool(payload.get("inspect_codex_environment", True)),
    )


def save_pre_vibe_settings(project_root: Path, settings: PreVibeSettings) -> dict[str, Any]:
    path = settings_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = asdict(settings)
    payload.pop("session_intensity", None)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"path": SETTINGS_PATH, "settings": payload}


def get_pre_vibe_settings(project_root: Path) -> dict[str, Any]:
    settings = load_pre_vibe_settings(project_root)
    session = SESSION_SETTINGS.get(project_key(project_root))
    if session and session.session_intensity:
        settings.session_intensity = session.session_intensity
    return asdict(settings)


def update_pre_vibe_settings(
    project_root: Path,
    *,
    default_intensity: str | None = None,
    allow_auto_upgrade: bool | None = None,
    architect_project_index: bool | None = None,
    inspect_codex_environment: bool | None = None,
) -> dict[str, Any]:
    settings = load_pre_vibe_settings(project_root)
    if default_intensity is not None:
        settings.default_intensity = coerce_intensity(default_intensity, "default_intensity")
    if allow_auto_upgrade is not None:
        settings.allow_auto_upgrade = bool(allow_auto_upgrade)
    if architect_project_index is not None:
        settings.architect_project_index = bool(architect_project_index)
    if inspect_codex_environment is not None:
        settings.inspect_codex_environment = bool(inspect_codex_environment)
    return save_pre_vibe_settings(project_root, settings)


def set_pre_vibe_intensity(project_root: Path, intensity: str) -> dict[str, Any]:
    selected = coerce_intensity(intensity)
    settings = load_pre_vibe_settings(project_root)
    settings.session_intensity = None if selected == "auto" else selected
    SESSION_SETTINGS[project_key(project_root)] = settings
    return {"session_intensity": selected, "settings": asdict(settings)}


def resolve_requested_intensity(project_root: Path, requested: str = "auto") -> tuple[str, PreVibeSettings]:
    settings = load_pre_vibe_settings(project_root)
    session = SESSION_SETTINGS.get(project_key(project_root))
    if requested != "auto":
        return coerce_intensity(requested), settings
    if session and session.session_intensity:
        settings.session_intensity = session.session_intensity
        return session.session_intensity, settings
    if settings.default_intensity != "auto":
        return settings.default_intensity, settings
    return "auto", settings
