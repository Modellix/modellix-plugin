# AGENTS.md

Agent instructions for maintaining and updating the **Modellix plugin** in this repository.

Human-facing overview lives in [README.md](README.md). This file is for coding agents working on the plugin package itself.

## Project overview

This repo publishes the Modellix plugin consumed by AI coding agents (Cursor, Claude Code, Codex, ClawHub, Smithery, Pi, Hermes, etc.). It follows the [Open Plugins specification](https://open-plugins.com/plugin-builders/specification): **the repository root is the plugin root**.

| Path | Role |
|------|------|
| [`.plugin/plugin.json`](.plugin/plugin.json) | **Vendor-neutral manifest** (primary source of plugin metadata) |
| [`.cursor-plugin/plugin.json`](.cursor-plugin/plugin.json) | Cursor manifest; also declares the `MODELLIX_API_KEY` variable |
| [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) | Claude Code manifest |
| [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) | Claude Code marketplace entry (`/plugin marketplace add`) |
| [`.codex-plugin/plugin.json`](.codex-plugin/plugin.json) | Codex manifest |
| [`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json) | Vendor-neutral / Codex marketplace entry |
| [`assets/logo.svg`](assets/logo.svg) | Plugin logo referenced by every manifest |
| [`skills/modellix/`](skills/modellix/) | **Skill package** (Open Plugins default discovery path) |
| [`skills/modellix/SKILL.md`](skills/modellix/SKILL.md) | Skill entrypoint (frontmatter + agent instructions) |
| [`skills/modellix/skill.json`](skills/modellix/skill.json) | Skill registry metadata (name, version, credentials) |
| [`skills/modellix/references/`](skills/modellix/references/) | Progressive disclosure playbooks (CLI / REST / capability matrix) |
| [`skills/modellix/scripts/`](skills/modellix/scripts/) | Optional Python helpers (thin wrappers around CLI / REST) |
| [`skills/modellix/assets/`](skills/modellix/assets/) | Schemas and other static assets |
| [`skills/modellix/evals/`](skills/modellix/evals/) | Eval prompts and assertions kept as a regression reference |
| [`.github/workflows/skill_update.yml`](.github/workflows/skill_update.yml) | On `main` push: sync Smithery, `npx skills add`, ClawHub skill + OpenClaw package |
| [`openclaw.plugin.json`](openclaw.plugin.json) | OpenClaw / ClawHub package manifest (skill bundle; no runtime extensions) |
| [`package.json`](package.json) | npm-style package metadata for ClawHub + Pi (`@modellix/modellix-plugin`, `pi.skills`) |
| [`.opencode/skills/modellix`](.opencode/skills/modellix) | Symlink to `skills/modellix` for [OpenCode Agent Skills](https://opencode.ai/docs/skills/) discovery |
| [`.pi/skills/modellix`](.pi/skills/modellix) | Symlink to `skills/modellix` for [Pi](https://github.com/badlogic/pi-mono) local skill discovery |
| [`.cursor/hooks.json`](.cursor/hooks.json) | After local `git push` to main: community listing check + agent follow-up |

There is no application runtime or test suite for a product app. The “product” is the plugin manifests + skill markdown + scripts.

Because `skills/` is an Open Plugins default discovery path, the Open Plugins manifests deliberately omit a `skills` field. Do not add one unless the skill moves. **Pi** and **Hermes** consume the same skill tree: Pi via `package.json#pi` / `pi install`; Hermes via `hermes skills install` / `~/.hermes/skills/` (or `skills.external_dirs`). Do not invent Hermes- or Pi-only plugin manifest directories.

Do not create top-level `commands/`, `agents/`, `rules/`, `hooks/`, `.mcp.json`, or `.lsp.json` unless you intend to ship those components: those paths are auto-discovered by plugin hosts. In particular, never put internal maintainer conventions in `rules/` — they would be installed into users' agents.

## Sources of truth (do not invent)

When updating CLI usage or model guidance, prefer live sources over memory or stale website pages:

1. **CLI behavior**: [npm `modellix-cli`](https://www.npmjs.com/package/modellix-cli) README and local `modellix-cli --help` / subcommand help.
2. **REST API**: https://docs.modellix.ai/ways-to-use/api.md
3. **Model index**: https://docs.modellix.ai/llms.txt — then fetch each model’s `.md` (or use `modellix-cli model describe <slug> --json` → `docs_url`).
4. **Plugin format**: https://open-plugins.com/plugin-builders/specification
5. **Do not** treat https://docs.modellix.ai/ways-to-use/cli.md as authoritative until it is updated to match the CLI package.
6. **Do not** reintroduce a bundled `references/REFERENCE.md` mirror of `llms.txt` (removed on purpose; it went stale and duplicated CLI/`llms.txt`).

Canonical agent workflow the skill teaches:

```text
doctor → (defaults or model list/describe) → model run --wait → task download
```

`model invoke` is only a compatibility alias of `model run`.

## Language and communication

- **English** for all repo artifacts: manifests, `SKILL.md`, playbooks, scripts, comments, commit messages, PR text.
- **Chinese** when chatting with the human maintainer (explanations, progress, questions).
- Keep technical terminology in its standard English form; quote code and logs unchanged and explain around them.
- Do not translate existing English content into Chinese unless explicitly requested.

## Setup for maintainers / agents

Optional but recommended when validating CLI changes:

```bash
npm i -g modellix-cli@latest
modellix-cli --version
export MODELLIX_API_KEY="..." # session only; never commit
modellix-cli doctor --json
```

Python helpers need a normal Python 3 interpreter (stdlib only; no pip deps required for `preflight.py` / `invoke_and_poll.py`).

```bash
python3 skills/modellix/scripts/preflight.py --json
python3 skills/modellix/scripts/clean_build_artifacts.py
```

## Plugin layout rules

Keep progressive disclosure tight:

- **`SKILL.md`**: policies, defaults, short examples, routing pointers. Prefer staying under ~500 lines.
- **`references/cli-playbook.md`**: full CLI command surface (auth, doctor, list/describe, run/wait/download, batch, recovery).
- **`references/rest-playbook.md`**: REST submit/poll only when CLI is unavailable.
- **`references/capability-matrix.md`**: CLI ↔ REST mapping and fallback rules.
- **`scripts/`**: optional; must not block the direct CLI path. Prefer wrapping native CLI (`doctor`, `model run --wait`, `task download`) over reinventing polling.

Paths inside the skill are relative to the **skill root** (`scripts/preflight.py`, `references/cli-playbook.md`). If something must resolve against the plugin root, use `${PLUGIN_ROOT}` (Claude Code also accepts `${CLAUDE_PLUGIN_ROOT}`). Never use `../` traversal outside the plugin.

[`.opencode/skills/modellix`](.opencode/skills/modellix) and [`.pi/skills/modellix`](.pi/skills/modellix) are **symlinks** to [`skills/modellix`](skills/modellix) so [OpenCode](https://opencode.ai/docs/skills/) and [Pi](https://github.com/badlogic/pi-mono) can discover the skill locally. Keep a single source of truth under `skills/modellix/`; do not duplicate the skill tree. OpenCode’s separate [plugins](https://opencode.ai/docs/zh-cn/plugins/) system (JS/TS hooks under `.opencode/plugins/`) is not used here. Hermes has no symlink dir in-repo — install `skills/modellix` via `hermes skills install` or into `~/.hermes/skills/`.

Install URLs:

```text
# Plugin (Claude Code / Codex marketplace)
Modellix/modellix-plugin

# Skill-only install (skills.sh)
npx skills add https://github.com/Modellix/modellix-plugin --skill modellix

# Pi package
pi install git:github.com/Modellix/modellix-plugin

# Hermes skill
hermes skills install Modellix/modellix-plugin/skills/modellix
```

## Manifest rules

- The four Open Plugins `plugin.json` files must stay in sync for shared metadata (`name`, `version`, `description`, `author`, `homepage`, `repository`, `license`, `logo`, `keywords`). Only the Cursor manifest carries the extra `variables` block.
- Keep `version` identical across those manifests, [`skills/modellix/skill.json`](skills/modellix/skill.json), and root [`package.json`](package.json).
- [`openclaw.plugin.json`](openclaw.plugin.json) is for ClawHub / OpenClaw. Keep `skills: ["./skills"]` and an empty `configSchema`. **Do not** add `openclaw.extensions` / runtime entrypoints unless intentionally shipping a native TypeScript OpenClaw code plugin (that would change detection from content bundle to code plugin).
- Root [`package.json`](package.json) also declares Pi packaging: keep `keywords` including `pi-package` and `"pi": { "skills": ["./skills"] }` in sync with the skill layout. Do not add Pi `extensions` unless shipping executable Pi extensions.
- Hermes-specific skill metadata lives in [`skills/modellix/SKILL.md`](skills/modellix/SKILL.md) frontmatter (`metadata.hermes`, `required_environment_variables`). Keep the long `description` for cross-host skill triggering; do not invent a second SKILL.md for Hermes. Optional short listing copy for directories: `Unified API for AI image and video generation`.
- `.plugin/plugin.json` is the primary Open Plugins source; edit it first, then mirror to vendor manifests.
- `name` must satisfy the Open Plugins spec: lowercase alphanumerics, hyphens, periods; no `--` or `..`.
- Manifest directories must contain only `plugin.json` (and, for Claude, `marketplace.json`). Components live at the plugin root.
- Never put credentials in a manifest; the Cursor `variables` block only declares the variable name.

## Default models policy

When the end user does not name a model, the skill must use these defaults (update the table in `SKILL.md` and keep examples/evals in sync):

| Task | Default slug |
|------|----------------|
| T2I | `google/nano-banana-2-lite` |
| T2V | `bytedance/seedance-2.0-mini-t2v` |
| I2I | `google/nano-banana-2-lite-edit` |
| I2V | `bytedance/seedance-2.0-fast-i2v` |
| V2V | `bytedance/seedance-2.0-fast-v2v` |

Verify slugs against OpenAPI / `model describe` (never invent from doc filenames). Changing defaults is a behavior change: bump the version everywhere and update evals.

## How to update the plugin (checklist)

### A) CLI package changed (new flags/commands)

1. Diff npm README / `modellix-cli --help` against `references/cli-playbook.md` and `SKILL.md` Execution Policy.
2. Update `capability-matrix.md` for new CLI-only capabilities.
3. Keep scripts aligned (`preflight.py` → `doctor`; `invoke_and_poll.py` → `model run --wait`, no paid-submit auto-retry).
4. Note paid-submit safety: unknown outcomes → `task history`, do not blind re-POST.
5. Note download quirk: if `task download` fails with private/reserved network (proxy DNS e.g. `198.18.0.0/15` for `file.modellix.ai`), document `--allow-private-network` or curl fallback for trusted Modellix CDN hosts.

### B) Default models or routing changed

1. Edit Default Models in `SKILL.md`.
2. Update examples in `SKILL.md` / playbooks / `skills/modellix/scripts/README.md` / root `README.md`.
3. Update [`skills/modellix/evals/evals.json`](skills/modellix/evals/evals.json) assertions.
4. Bump `version` in the four manifests and [`skills/modellix/skill.json`](skills/modellix/skill.json) (semver: patch for docs/typos, minor for workflow/default changes, major for breaking install or skill contract changes).

### C) REST-only or schema guidance

1. Prefer linking to live model docs via `llms.txt` / `docs_url`.
2. Update `rest-playbook.md` only for shared REST semantics (auth, poll statuses, retry).

### D) Before finishing an edit

- [ ] No secrets (`MODELLIX_API_KEY`, profiles) in files or examples that echo real keys.
- [ ] No reintroduction of `REFERENCE.md` or the deleted `sync_ref_mint_llmstxt` workflow.
- [ ] Manifests still in sync (metadata + version) and valid JSON.
- [ ] Root README install/credential/execution sections still match `SKILL.md`.
- [ ] `python3 -m py_compile skills/modellix/scripts/*.py`
- [ ] `python3 skills/modellix/scripts/clean_build_artifacts.py`

## Testing / smoke checks

There is no unit-test runner. Validate with:

1. **Manifest validity**:

```bash
python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('.*-plugin/*.json') + ['.plugin/plugin.json', '.agents/plugins/marketplace.json']]"
```

2. **Plugin load**:

```bash
claude plugin validate .            # Claude Code
claude --plugin-dir .               # local run
ln -s "$PWD" ~/.cursor/plugins/local/modellix   # Cursor, then Reload Window
codex plugin marketplace add "$PWD" # Codex, local path
```

3. **CLI smoke** (needs key + balance):

```bash
modellix-cli doctor --json
modellix-cli model run \
 --model-slug google/nano-banana-2-lite \
 --body '{"prompt":"smoke test"}' \
 --wait --timeout 5m --json
# if download fails on private network:
modellix-cli task download <task_id> --output-dir ./tmp-out --json --allow-private-network
```

4. **Script smoke**:

```bash
python3 skills/modellix/scripts/preflight.py --json
```

[`skills/modellix/evals/evals.json`](skills/modellix/evals/evals.json) keeps prompts and assertions for default-model and CLI-flow regressions. The `skill-creator` tooling that used to run them is no longer vendored here; run evals with your own harness and keep run artifacts out of the repo.

Do not commit API keys. Prefer session env or `/tmp` env files with mode `600`, then delete.

## Code style

- Markdown: clear imperative instructions; explain *why* for non-obvious rules; avoid ALL-CAPS MUST spam.
- Python: stdlib only, cross-platform, type hints welcome; fail with stderr + non-zero exit.
- JSON: two-space indent, trailing newline.
- Examples: prefer `--json` / machine-readable output; redact secrets as `<MODELLIX_API_KEY>` or omit.
- Keep the skill triggering description in frontmatter “pushy” enough to fire on Modellix / generation tasks, but accurate.

## Security

- Never commit credentials, `.env`, or profile files with keys.
- The skill must default to session-only credentials; persistent write only on explicit user request (`auth login` / `init` preferred over writing other agents’ configs).
- Do not log or print API keys in transcripts, eval outputs, or README examples.
- Network egress for the plugin is Modellix API / CDN / docs (`api.modellix.ai`, `file.modellix.ai`, `docs.modellix.ai`).

## CI / publish

On push to `main`, [`skill_update.yml`](.github/workflows/skill_update.yml):

1. `PUT` Smithery skill `modellix/modellix-skill` with the git URL of `skills/modellix/` (requires `SMITHERY_TOKEN` secret). The Smithery slug stays `modellix-skill` to preserve existing installs; only the git URL changed.
2. After 60s, runs `npx skills add https://github.com/Modellix/modellix-plugin --skill modellix`.
3. Publishes `skills/modellix` to ClawHub as skill `modellix/modellix` via [`skill-publish.yml`](https://github.com/openclaw/clawhub/blob/main/.github/workflows/skill-publish.yml) (requires `CLAWHUB_TOKEN`).
4. Publishes the repo root as OpenClaw **bundle-plugin** package `@modellix/modellix-plugin` via [`package-publish.yml`](https://github.com/openclaw/clawhub/blob/main/.github/workflows/package-publish.yml) (same token). This is a content/skill bundle (`openclaw.plugin.json` + Open Plugins manifests), not a code plugin with `openclaw.extensions`.

OpenClaw install paths:

```bash
clawhub install modellix                                 # skill
openclaw plugins install clawhub:@modellix/modellix-plugin  # bundle plugin
```

Before changing OpenClaw package metadata, run:

```bash
npx clawhub@latest package validate .
npx clawhub@latest package publish . --family bundle-plugin --owner modellix --dry-run --json
```

Agents editing the plugin do not need to trigger publish manually; merging to `main` does. Claude Code / Codex marketplaces read the repository directly, so no extra publish step is required for them.

## Pull requests and commits

- Commit / PR language: **English**.
- Prefer focused commits: skill behavior vs docs-only vs scripts vs plugin packaging.
- Suggested title patterns:
 - `feat(plugin): ...` — packaging, manifests, marketplace
 - `feat(skill): ...` — new CLI capability or workflow
 - `fix(skill): ...` — incorrect defaults, flags, or safety
 - `docs: ...` — playbook/README clarity
 - `chore: bump version to x.y.z`
- Before merge: run the relevant smoke checks above; ensure version bump if behavior changes.

## Common gotchas

- Website CLI docs may lag the npm CLI — trust npm/`--help`.
- `task download` may need `--allow-private-network` on machines whose DNS maps CDN hosts into proxy ranges (`198.18.0.0/15`).
- Paid `model run` must not be auto-retried on ambiguous/unknown submission outcomes.
- Filename ≠ model slug (e.g. docs path `seedance-2-0-mini-t2v.md` vs slug `bytedance/seedance-2.0-mini-t2v`).
- Plugin root is the repo root; the skill-only install path is `skills/modellix`, not the repo root and not a nested package directory.
- Version lives in the four Open Plugins manifests + `skills/modellix/skill.json` + root `package.json` (+ Claude marketplace `metadata.version`); bump them together.

## Quick file map for edits

| Change type | Touch first |
|-------------|-------------|
| Plugin metadata / logo / keywords | `.plugin/plugin.json` then mirror to the three vendor manifests |
| Marketplace listing | `.agents/plugins/marketplace.json`, `.claude-plugin/marketplace.json` |
| Default models | `skills/modellix/SKILL.md`, examples, `skills/modellix/evals/evals.json`, version bump |
| CLI workflow | `skills/modellix/SKILL.md`, `skills/modellix/references/cli-playbook.md`, `capability-matrix.md`, scripts |
| REST fallback | `skills/modellix/references/rest-playbook.md`, `capability-matrix.md` |
| Install / registry copy | root `README.md`, manifests, `skills/modellix/skill.json` |
| Pi package metadata | root `package.json` (`pi-package`, `pi.skills`); keep `.pi/skills/modellix` symlink |
| Hermes skill metadata | `skills/modellix/SKILL.md` frontmatter (`metadata.hermes`, `required_environment_variables`); README Hermes install |
| Eval prompts | `skills/modellix/evals/evals.json` |

## Listing the plugin in external directories

After a successful `git push` to `main`, a **project Cursor hook** refreshes this work so agents do not need the old long playbook in this file:

| Piece | Role |
|-------|------|
| [`.cursor/hooks.json`](.cursor/hooks.json) | `afterShellExecution` on `git push` + `stop` follow-up |
| [`.cursor/hooks/community-listings.json`](.cursor/hooks/community-listings.json) | Canonical URLs, target repos, desired snippets, PR titles |
| [`.cursor/hooks/sync_community_listings.py`](.cursor/hooks/sync_community_listings.py) | `--check` / `--apply` against those targets |
| [`.cursor/hooks/after_git_push.py`](.cursor/hooks/after_git_push.py) | Detects successful main push, runs `--check`, writes pending state |
| [`.cursor/hooks/on_stop_listings.py`](.cursor/hooks/on_stop_listings.py) | On agent stop, emits a one-shot `followup_message` to act on the report |

Manual check anytime:

```bash
python3 .cursor/hooks/sync_community_listings.py --check
python3 .cursor/hooks/sync_community_listings.py --apply   # stale readme_link PRs via gh
```

Rules that stay here (hooks enforce the rest):

- Listing PR titles/bodies/commits in **other** repos must be **English**.
- Chat with the human maintainer about PR URLs may be Chinese.
- Do not invent listing targets: edit `community-listings.json` when URLs or directories change.
- Official plugin markets (`manual_channels` in that JSON) stay human-submitted; the hook only reminds.

Canonical links live in `community-listings.json` → `canonical` (skill URL, repo URL, ClawHub, etc.).
