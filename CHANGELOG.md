# Changelog

All notable changes to this project are documented here. The format loosely follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions use [Semantic Versioning](https://semver.org/).

## [3.4.0] - 2026-07-27

### Added

- Open Plugins always-on rules under [`rules/`](rules/): `cli-and-defaults.mdc`, `paid-submit-safety.mdc`, and `credentials-and-docs.mdc` (short session guardrails; full playbooks stay in `skills/modellix/`).

## [3.3.0] - 2026-07-27

### Added

- Open Plugins Docs MCP via root [`.mcp.json`](.mcp.json) pointing at the remote server https://docs.modellix.ai/mcp (`modellix-docs`). Read-only documentation search/filesystem tools only — not generation, auth, or downloads.
- Skill / capability-matrix / README / AGENTS guidance: prefer Docs MCP for product/API/schema lookup when connected; keep CLI npm/`--help` as the source of truth for CLI flags; execution policy stays in `skills/modellix/SKILL.md`.

## [3.2.2] - 2026-07-27

### Changed

- `homepage` in the four Open Plugins manifests and root `package.json` now points at the plugin guide (https://docs.modellix.ai/ways-to-use/plugin) instead of the skill-only guide.
- README links to the published plugin guide; AGENTS.md records it as a source of truth to keep in sync with the install sections.
- `.cursor/hooks/community-listings.json` carries `docs_plugin` / `docs_skill` canonical URLs for directory listings.

## [3.2.1] - 2026-07-27

### Added

- Pi package support: `package.json` `keywords` include `pi-package`, `"pi": { "skills": ["./skills"] }`, and `.pi/skills/modellix` → `skills/modellix` symlink for local discovery.
- Hermes Agent skill metadata in `SKILL.md`: `metadata.hermes.tags` and `required_environment_variables` for `MODELLIX_API_KEY` (secure prompt / `~/.hermes/.env`).
- README / AGENTS install docs for Pi (`pi install git:github.com/Modellix/modellix-plugin`) and Hermes (`hermes skills install …`, symlink / `external_dirs`).

### Notes

- Pi and Hermes consume the skill tree (and Pi package metadata); they are not Open Plugins marketplace hosts. Long skill `description` is unchanged for cross-host triggering; short listing blurb for Hermes directories: `Unified API for AI image and video generation`.

## [3.2.0] - 2026-07-27

### Added

- OpenClaw / ClawHub **bundle-plugin** packaging: root `package.json` (`@modellix/modellix-plugin`) and `openclaw.plugin.json` declaring `./skills` (content/skill bundle, no `openclaw.extensions` runtime).
- `skill_update.yml` publishes the package via ClawHub `package-publish.yml` alongside the existing skill publish.
- README / AGENTS install docs for `openclaw plugins install clawhub:@modellix/modellix-plugin` and the existing `clawhub install modellix` skill path.
- OpenCode Agent Skills discovery via `.opencode/skills/modellix` → `skills/modellix` symlink (OpenCode plugins are a separate JS/TS hook system; Modellix ships as a skill).

### Notes

- `clawhub package validate` may report a P2 `package-openclaw-entry-missing` warning because this package intentionally has no runtime entrypoint. That is expected for a skill/content bundle.

## [3.1.0] - 2026-07-27

### Changed

- Updated default models: Image editing / I2I is now `google/nano-banana-2-lite-edit` (was `bytedance/seedream-5.0-lite-edit`); Video-to-video (V2V) is now `bytedance/seedance-2.0-fast-v2v` (was `bytedance/seedance-2.0-v2v`).
- Updated `SKILL.md`, `references/capability-matrix.md`, `README.md`, and `AGENTS.md` default-model tables and examples to match.
- Prefer `npx skills add https://github.com/Modellix/modellix-plugin --skill modellix` for Agent Skills installs.
- `skill_update.yml` also publishes to ClawHub via the reusable skill-publish workflow (`CLAWHUB_TOKEN`).
- Added project Cursor hooks that, after a successful `git push` to main, check external skill-directory listings and follow up via `stop` (`community-listings.json` is now the source of truth; the long AGENTS.md playbook was removed).

## [3.0.0] - 2026-07-27

### Changed

- **Breaking (install paths):** the repository is now an [Open Plugins](https://open-plugins.com/plugin-builders/specification) package. The repository root is the plugin root and the skill moved from `modellix-skill/` to `skills/modellix/`.
- Skill-only install is now `npx skills add https://github.com/Modellix/modellix-plugin --skill modellix`.
- `.github/workflows/skill_update.yml` publishes the new path to Smithery, runs `npx skills add ... --skill modellix`, and publishes `skills/modellix` to ClawHub (`modellix/modellix`). The Smithery registry slug (`modellix/modellix-skill`) is unchanged so existing installs keep resolving.
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
