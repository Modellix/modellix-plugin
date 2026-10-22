# Changelog

All notable changes to this project are documented here. The format loosely follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions use [Semantic Versioning](https://semver.org/).

## [4.12.0] - 2026-10-22

### Added

- Add `skills/modellix-article-illustrator` to plan a set of illustrations placed through an article. It confirms type, style, palette, density, aspect, and language, writes one prompt per illustration, and hands generation to `modellix-design`. It does not recommend a model or submit a task.

### Changed

- Route an in-article illustration set from `modellix-image-prompt-engineering`, `modellix-infographic`, `modellix-cover-image`, `modellix-comic`, and `modellix-social-card` to `modellix-article-illustrator`.

## [4.11.0] - 2026-10-22

### Added

- Add `skills/modellix-comic` to plan a knowledge comic, educational comic, biography comic, or four-panel strip. It confirms the style, page count, aspect, language, and text level, locks the cast, writes one prompt per page, and hands generation to `modellix-design`. It does not recommend a model or submit a task.

### Changed

- Route a knowledge comic that still needs a storyboard from `modellix-image-prompt-engineering`, `modellix-infographic`, `modellix-cover-image`, and `modellix-social-card` to `modellix-comic`.

## [4.10.0] - 2026-10-22

### Added

- Add `skills/modellix-cover-image` to plan one article, blog, or newsletter cover. It confirms type, palette, rendering, text level, mood, and font, quotes the source title, and hands generation to `modellix-design`. It does not recommend a model or submit a task.

### Changed

- Route an article cover with no named network from `modellix-social-card`, `modellix-image-prompt-engineering`, and `modellix-infographic` to `modellix-cover-image`.

## [4.9.0] - 2026-10-22

### Added

- Add `skills/modellix-ecomm-ugc-video` to plan a vertical ecommerce UGC video. It confirms the pattern, quotes only supplied product facts, writes one prompt per shot, and hands generation to `modellix-design`. On-screen captions are listed for `modellix-ffmpeg` after the shots exist. It does not recommend a model or submit a task.

### Changed

- Route a commerce UGC video that still needs a shot plan from `modellix-image-prompt-engineering`, `modellix-social-card`, `modellix-infographic`, `modellix-ffmpeg`, and `modellix-moviepy` to `modellix-ecomm-ugc-video`.

## [4.8.0] - 2026-10-22

### Added

- Declare Modellix Web Tools in `mcp.json` and `.mcp.json` without auth headers. The server at `https://tool.modellix.ai/mcp` exposes billed public web search and URL fetch. The host attaches the API key.

## [4.7.0] - 2026-10-22

### Added

- Add `skills/modellix-infographic` to plan one infographic prompt from a source. It confirms the information structure, quotes the source facts, and hands generation to `modellix-design`. It does not recommend a model or submit a task.

### Changed

- Route a structured infographic from `modellix-social-card` and `modellix-image-prompt-engineering` to `modellix-infographic`.

## [4.6.0] - 2026-10-21

### Added

- Add `skills/modellix-social-card` to plan prompts for mainstream social cards, covers, and carousels. It writes one prompt per placement and hands generation to `modellix-design`. It does not recommend a model or submit a task.

## [4.5.0] - 2026-10-21

### Added

- Add `skills/modellix-ffmpeg` for local concatenation, trimming, reframing, and transcoding after files are on disk. `scripts/check_ffmpeg.py --json` reports whether FFmpeg is usable and prints a platform install command. It does not install FFmpeg, download a binary, or call Modellix.
- Add `skills/modellix-moviepy` for titles, lower thirds, and timed composites after files are on disk. `scripts/check_moviepy.py --json` reports whether moviepy 2.x and Pillow import and prints a pip command. It does not install them or call Modellix.

### Fixed

- Document all four skills in the install instructions. `modellix-ffmpeg` and `modellix-moviepy` ship with the plugin package, not as separate Smithery or ClawHub skills.

## [4.4.0] - 2026-10-21

### Changed

- Remove built-in default models from `modellix-design`. If the user does not name a `provider/model` slug, ask and wait. Do not invent one.
- Stop recommending image models from `modellix-image-prompt-engineering`. That skill writes the prompt and leaves model choice to the user.

## [4.3.0] - 2026-10-21

### Added

- Declare Modellix Docs Search and Modellix Media Generation in `mcp.json` and `.mcp.json` without auth headers.
- Route `modellix-design` through Media Generation when its tools are available and the input is not a local file, then the CLI, then REST.
- Ask on Cursor before a repeated `modellix_submit_task` for a model slug already submitted in the session.

### Changed

- Rename the docs MCP server key from `modellix-docs` to `Modellix Docs Search`.

## [4.2.2] - 2026-10-15

### Fixed

- Enforce the overall REST wait budget during slow response headers and bodies, proxy CONNECT, and TLS handshakes.
- Stop timed-out socket I/O and retain the task ID for recovery without another paid submission.

## [4.2.1] - 2026-10-15

### Fixed

- Reject authenticated REST redirects so credentials never reach a different origin.
- Preserve HTTP failure codes without reading or echoing untrusted error bodies.
- Treat invalid paid-submit responses and missing task IDs as unknown outcomes, without replaying the request.

## [4.2.0] - 2026-10-15

### Changed

- Use bounded server-side waits in the REST helper with one monotonic deadline.
- Document CLI 0.0.11 file listing, media formats, quota recovery, and unfinished task snapshots.
- Preserve CLI-first execution, paid-submit guards, and the separate prompt-only skill.

## [4.1.0] - 2026-09-16

### Added

- Added the English `modellix-image-prompt-engineering` Agent Skill for image art
  direction, high-density prompt writing, grid briefs, and prompt-side failure
  diagnosis before generation.
- Added `/modellix:prompt` for preparing a T2I or I2I brief without submitting a
  paid task.

### Changed

- Vague image requests now flow through the prompt-engineering skill before
  `modellix-design`; complete prompts can still go directly to execution.
- Plugin and execution-skill metadata version is now `4.1.0`. The prompt-only
  skill starts its independent version at `1.0.0`.

## [4.0.0] - 2026-09-16

### Changed

- **Breaking (skill identity):** renamed the Agent Skill from `modellix` to `modellix-design`. The skill tree is now [`skills/modellix-design/`](skills/modellix-design/). Skill-only installs must use `--skill modellix-design`. The ClawHub skill slug is `modellix/modellix-design`. Plugin name, slash commands (`/modellix:*`), and the Smithery registry slug (`modellix/modellix-skill`) are unchanged.
- Plugin and skill metadata version is now `4.0.0`.

## [3.10.0] - 2026-09-04

### Added

- Skill and CLI playbook coverage for `modellix-cli model get-schema`, the public request/response contract used to build `--body` before a paid submit.

### Changed

- Schema lookup prefers `model get-schema` over Docs MCP / `describe` → `docs_url` when the CLI is available. `model describe` remains catalog metadata.
- `/modellix:models`, paid commands, credentials rule, README, and AGENTS.md now route schema questions to `get-schema`.
- Plugin and skill metadata version is now `3.10.0`.

## [3.9.1] - 2026-08-12

### Added

- Public npm distribution for the complete Agent Plugins bundle, including a cross-platform `npx @modellix/modellix-plugin install` command for Cursor local installs and portable directory materialization.
- Direct npm install instructions for Pi and OpenClaw, plus npm publication in the main release workflow.
- Installer regression coverage for explicit host selection, dry runs, portable bundle contents, and repository-file exclusions.

### Changed

- Plugin and skill metadata version is now `3.9.1`.

## [3.9.0] - 2026-08-12

### Added

- Agent Plugins 1.0.0 portable core with schema-declared root `plugin.json`, fixed `skills/` discovery, and root `mcp.json` using the current Streamable HTTP transport.
- Automatic `modellix-cli` preflight: compare against the public npm `latest` tag, install a newer exact version before execution, never downgrade, and pin the resolved executable through the paid workflow.
- Regression coverage for Agent Plugins layout, CLI version validation, exact-version updates, offline fallback, and downgrade prevention.

### Changed

- Host-specific Cursor, Claude, Codex, legacy Open Plugins, rules, commands, hooks, and `.mcp.json` files are documented as adapters layered on the portable Agent Plugins core.
- Plugin and skill metadata version is now `3.9.0`.

## [3.8.0] - 2026-08-05

### Added

- `/modellix:audio` for TTS, STT, and STS workflows, plus audio-aware skill triggers, metadata, supported-task documentation, and repository regression tests.
- Cursor Marketplace metadata (`displayName`, publisher, category, tags, explicit components, and `.cursor-plugin/marketplace.json`) aligned with the official Cursor schemas.
- Cross-platform `scripts/run_python_hook.mjs`, which locates Python 3 on Windows, macOS, or Linux and keeps optional hooks fail-open.

### Fixed

- Paid REST submissions are sent exactly once; only safe task-status reads retry transient `408`/`429`/`5xx` responses and transport failures.
- Hook state no longer persists the original CLI command or request body, preventing user prompts from being written to the temporary state file.
- Hook result detection uses shell exit codes and structured JSON so successful output containing `"error": null` is not treated as failed.
- Paid-attempt counters are recorded only after shell execution, so a rejected confirmation is never mistaken for a submitted task.
- Explicit CLI API keys are passed through the child environment rather than process arguments.
- The task-result schema now accepts CLI raw output and the optional download result.
- Preflight no longer recommends execution after a failed `modellix-cli doctor` check or echoes malformed doctor output.
- The vendor-neutral Open Plugins `name` is lowercase again, restoring v1.0 identifier conformance while Cursor uses `displayName` for presentation.

### Security

- Removed repository-level `.cursor/hooks.json` and community-listing scripts that injected unrelated assistant follow-ups and caused the Cursor Directory security scan to hide the plugin.
- Pinned GitHub Actions and the ClawHub reusable workflow to immutable commit SHAs, with read-only default workflow permissions.

## [3.7.0] - 2026-07-29

### Added

- Default models when the user omits a slug for speech tasks: TTS `alibaba/qwen-audio-3.0-tts-flash`, STT `openai/whisper-1`, STS `alibaba/cosyvoice-clone` (synced across `SKILL.md`, rules, playbooks, README, AGENTS, evals).

## [3.6.0] - 2026-07-27

### Added

- Open Plugins commands component under [`commands/`](commands/): `/modellix:image`, `/modellix:video`, `/modellix:doctor`, `/modellix:models`, `/modellix:tasks`, `/modellix:download`. Each is a thin prompt that routes arguments to the existing `modellix-cli` flow; execution policy stays in `skills/modellix/SKILL.md` and `rules/`.
- The two paid commands (`image`, `video`) set `disable-model-invocation: true`, so only a human can trigger a charge through a command.

### Changed

- `package.json` publishes `commands/**`; README and AGENTS.md document the command set and its authoring invariants.

## [3.5.0] - 2026-07-27

### Added

- Open Plugins hooks component: [`hooks/hooks.json`](hooks/hooks.json) for Open Plugins / Claude Code event names and [`hooks/cursor-hooks.json`](hooks/cursor-hooks.json) for Cursor, wired through the matching `plugin.json` so a host loads only one config.
- Plugin-level [`scripts/`](scripts/) hook implementations (stdlib Python): confirmation prompt for repeated paid submits and for `model batch` without `--max-tasks`, task-id tracking, and a single stop-time reminder to download results before the 7-day expiry.

### Changed

- `package.json` publishes `hooks/**` and `scripts/**`; README and AGENTS.md document hook behavior, the two-config split, and the plugin-level vs skill-level `scripts/` distinction.
- `skills/modellix/scripts/clean_build_artifacts.py` now cleans the whole plugin tree when run from the repo, and stays scoped to the skill directory for standalone skill installs.

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
