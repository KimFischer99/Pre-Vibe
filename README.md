# pre-vibe

This repository contains the source package for the `pre-vibe` Codex plugin.

The public-ready plugin package lives in `pre-vibe-plugin/`. The current architecture
report lives in `architecture.md`.

pre-vibe is designed as a first-session intake workflow for Codex. It clarifies rough
user requests, performs mandatory safe project and Codex-component indexing before
questions, writes a beginner-friendly handbook spec plus agent-facing guidance, clears
context after user approval, and then injects only a compact first prompt.

The plugin package also includes a slash prompt source so local installs can expose
pre-vibe from Codex's slash command picker on supported CLI/app surfaces.
