# Changelog

All notable changes to this project are documented here. The format loosely follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions use [Semantic Versioning](https://semver.org/).

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
