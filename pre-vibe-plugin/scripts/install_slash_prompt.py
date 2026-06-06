#!/usr/bin/env python3
"""Install the pre-vibe slash prompt command into the local Codex home."""

from __future__ import annotations

import argparse
import os
from pathlib import Path


def install(plugin_root: Path, codex_home: Path) -> Path:
    source = plugin_root / "prompts" / "pre-vibe.md"
    if not source.exists():
        raise FileNotFoundError(f"missing slash prompt source: {source}")
    target_dir = codex_home / "prompts"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "pre-vibe.md"
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    return target


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install pre-vibe slash prompt command.")
    parser.add_argument("--plugin-root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--codex-home", default=os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target = install(Path(args.plugin_root).expanduser().resolve(), Path(args.codex_home).expanduser().resolve())
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
