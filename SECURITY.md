# Security Policy

Pre-Vibe reads project metadata and allowlisted project files to prepare Codex starting context. It is designed to skip secret-like files by default, including environment files, private keys, token stores, databases, dumps, and production logs.

## Reporting

Please do not post secrets, private repositories, proprietary binaries, or sensitive project output in public issues.

For security concerns, use GitHub's private vulnerability reporting flow if it is enabled for this repository. If private reporting is unavailable, open a public issue with a minimal description that does not include sensitive data, and the maintainer can move the discussion to a safer channel.

## Supported Versions

Only the latest commit on `main` is supported during this early plugin phase.
