# Changelog

All notable changes to this project are documented here. The format loosely follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions use [Semantic Versioning](https://semver.org/).

## [3.0.0] - 2026-07-27

### Changed

- **Breaking (install paths):** the repository is now an [Open Plugins](https://open-plugins.com/plugin-builders/specification) package. The repository root is the plugin root and the skill moved from `modellix-skill/` to `skills/modellix/`.
- Skill-only install URL is now `https://github.com/Modellix/modellix-plugin/tree/main/skills/modellix`.
- `.github/workflows/skill_update.yml` publishes the new path. The Smithery registry slug (`modellix/modellix-skill`) is unchanged so existing installs keep resolving.
- Repository renamed to `Modellix/modellix-plugin`; all documentation URLs updated.

### Added

- Plugin manifests: `.plugin/plugin.json` (primary), `.cursor-plugin/plugin.json` (declares the `MODELLIX_API_KEY` variable), `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`.
- Marketplace entries for Claude Code (`.claude-plugin/marketplace.json`) and Codex / vendor-neutral hosts (`.agents/plugins/marketplace.json`), enabling `/plugin marketplace add Modellix/modellix-plugin` and `codex plugin marketplace add Modellix/modellix-plugin`.
- `assets/logo.svg` referenced by every manifest.
- This changelog.

### Removed

- Vendored `skill-creator` tooling under `.agents/skills/`, the `skills-lock.json` that tracked it, and the internal `.cursor/rules/` writing conventions (the language policy now lives in `AGENTS.md`).

## [2.1.0] - earlier

- Skill-only releases published from `modellix-skill/`. See git history for details.
