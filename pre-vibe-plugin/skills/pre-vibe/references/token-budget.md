# Intensity Profiles

This file remains for compatibility with older references. v0.4 no longer treats token
counts as strict budgets. Use intensity profiles to control workflow effort, then keep
the first prompt minimal.

| Intensity | Behavior |
|---|---|
| `mini` | Mandatory lightweight project/component index; up to 3 blocking questions; no fetch by default. |
| `default` | Mandatory light allowlist scan and component index; up to 5 blocking questions; fetch only when useful. |
| `architect` | Mandatory broader scan/component index; up to 10 blocking questions in staged rounds; broader fetch; full handbook when the task needs it. |

Compression rule for `FIRST_PROMPT.md`:

1. Remove rationale.
2. Remove examples.
3. Collapse background into assumptions.
4. Replace summaries with file/source pointers.
5. Narrow the current task.
