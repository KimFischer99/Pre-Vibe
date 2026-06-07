# Contributing

Thanks for helping improve Pre-Vibe.

## Development Setup

Use Python 3 and run checks from the repository root:

```bash
claude plugin validate plugins/pre-vibe --strict
python3 -m py_compile plugins/pre-vibe/scripts/*.py
python3 -m unittest discover -s tests
```

## Pull Requests

- Keep changes focused on the requested behavior.
- Update docs when workflow behavior changes.
- Add tests for routing, artifact validation, or handoff behavior when touching those paths.
- Do not commit generated Pre-Vibe project artifacts.

## Release Checklist

1. Update `CHANGELOG.md`.
2. Keep `plugin.json`, MCP server info, and README badges on the same public version.
3. Run validation and tests.
4. Test locally with `claude --plugin-dir ./plugins/pre-vibe` and sanity-check startup behavior.
5. Create and push the plugin release tag with `claude plugin tag plugins/pre-vibe --push`.
6. Create a GitHub Release from that tag and copy the changelog entry into the release notes.
