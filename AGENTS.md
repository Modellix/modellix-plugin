# AGENTS.md

Instructions for coding agents that maintain this **Modellix plugin** package. Human install and product overview live in [README.md](README.md).

## Project overview

This repository is an [Open Plugins](https://open-plugins.com/plugin-builders/specification) **v1** plugin: **the git repository root is the plugin root**. It ships one Agent Skill at `skills/modellix/` for Modellix image/video generation (CLI-first, REST fallback), plus a read-only **Docs MCP** at `.mcp.json`. Hosts that consume it include Cursor, Claude Code, Codex, OpenClaw/ClawHub, OpenCode, Pi, Hermes, and any Agent Skills host.

There is no application runtime or unit-test suite. The product is manifests + skill markdown + thin Python helpers.

```text
modellix-plugin/                 ← plugin root (= repo root)
├── .plugin/plugin.json          ← vendor-neutral Open Plugins manifest (edit first)
├── .cursor-plugin/plugin.json   ← Cursor (+ MODELLIX_API_KEY variables)
├── .claude-plugin/              ← Claude Code plugin.json + marketplace.json
├── .codex-plugin/plugin.json
├── .agents/plugins/marketplace.json
├── assets/logo.svg
├── skills/modellix/             ← Open Plugins default skills/ discovery
│   ├── SKILL.md
│   ├── skill.json
│   ├── references/              ← cli / rest / capability playbooks
│   ├── scripts/                 ← optional CLI wrappers (stdlib Python)
│   ├── assets/
│   └── evals/
├── openclaw.plugin.json         ← ClawHub bundle-plugin (skills only; no extensions)
├── .mcp.json                    ← Docs MCP → https://docs.modellix.ai/mcp (search/read docs only)
├── rules/                       ← Open Plugins always-on .mdc guardrails
├── package.json                 ← ClawHub + Pi (`pi-package`, pi.skills)
├── .opencode/skills/modellix → ../../skills/modellix
├── .pi/skills/modellix → ../../skills/modellix
└── .github/workflows/skill_update.yml
```

## Open Plugins conformance

Follow https://open-plugins.com/plugin-builders/specification (and marketplace/install docs on the same site). Rules that matter here:

1. **Plugin root = repo root.** All component paths are relative to that root and use `./…`. Never `../` outside the plugin tree.
2. **Manifests:** Prefer `.plugin/plugin.json` as the source of truth; keep vendor copies (`.cursor-plugin/`, `.claude-plugin/`, `.codex-plugin/`) in sync for shared metadata. Each metadata directory contains **only** `plugin.json` (Claude may also have `marketplace.json`). Components live at the plugin root, not inside `.plugin/`.
3. **Default discovery:** Hosts load `skills/` automatically. Because the skill lives at `skills/modellix/`, Open Plugins manifests **omit** a `skills` field — do not add one unless the skill moves off the default path.
4. **Do not invent unused components.** Never create top-level `commands/`, `agents/`, `hooks/`, or `.lsp.json` unless you intend to ship them (hosts auto-discover those paths). This plugin **does** ship `.mcp.json` (Docs MCP) and `rules/*.mdc` (always-on guardrails). Maintainer Cursor hooks stay under `.cursor/hooks/` — that is **not** an Open Plugins `hooks/` component.
5. **Names:** `name` is lowercase alphanumerics, hyphens, periods; no `--` or `..`. Current name: `modellix`.
6. **`${PLUGIN_ROOT}`** (Claude also accepts `${CLAUDE_PLUGIN_ROOT}`) for paths that must resolve against the plugin root. Skill-internal refs stay relative to the skill root (`scripts/…`, `references/…`).
7. **Pi / Hermes** reuse the same `skills/modellix` tree (Pi via `package.json#pi` / symlink; Hermes via skill install + SKILL.md frontmatter). Do not invent Pi-/Hermes-only Open Plugins manifest directories.

## Sources of truth

Do not invent CLI flags, model slugs, or install paths from memory:

1. **CLI:** [npm `modellix-cli`](https://www.npmjs.com/package/modellix-cli) + local `modellix-cli --help`
2. **REST:** https://docs.modellix.ai/ways-to-use/api.md
3. **Models:** https://docs.modellix.ai/llms.txt → model `.md` / `modellix-cli model describe <slug> --json`
4. **Docs search (optional host MCP):** https://docs.modellix.ai/mcp via plugin [`.mcp.json`](.mcp.json) — documentation only; not generation
5. **Plugin format:** https://open-plugins.com/plugin-builders/specification
6. **Published install guide:** https://docs.modellix.ai/ways-to-use/plugin.md (flag drift vs README when install/defaults change)
7. Do **not** treat `docs.modellix.ai/ways-to-use/cli.md` as authoritative until it matches the npm CLI
8. Do **not** reintroduce `references/REFERENCE.md` mirroring `llms.txt`

Skill workflow to teach:

```text
doctor → (defaults or model list/describe) → model run --wait → task download
```

`model invoke` is only a compatibility alias of `model run`.

## Language

- **English** for all repo artifacts (manifests, SKILL.md, playbooks, scripts, commits, PR text, external listing PRs).
- **Chinese** when chatting with the human maintainer.
- Do not translate existing English content unless asked.

## Setup

```bash
npm i -g modellix-cli@latest
export MODELLIX_API_KEY="..."   # session only; never commit
modellix-cli doctor --json
python3 skills/modellix/scripts/preflight.py --json
python3 skills/modellix/scripts/clean_build_artifacts.py
```

Python helpers: stdlib only (no pip deps for `preflight.py` / `invoke_and_poll.py`).

## Layout and skill rules

Progressive disclosure:

| Path | Role |
|------|------|
| `SKILL.md` | Policies, defaults, short examples; prefer staying under ~500 lines |
| `references/cli-playbook.md` | Full CLI surface |
| `references/rest-playbook.md` | REST only when CLI unavailable |
| `references/capability-matrix.md` | CLI ↔ REST mapping |
| `scripts/` | Optional; must not block the direct CLI path |

Keep a **single** skill tree under `skills/modellix/`. `.opencode/skills/modellix` and `.pi/skills/modellix` are symlinks only — do not duplicate. OpenCode’s JS/TS `.opencode/plugins/` system is unused here.

## Manifest rules

- Keep shared metadata in sync across the four Open Plugins `plugin.json` files, `skills/modellix/skill.json`, and root `package.json` (`name`/`version`/`description`/`homepage`/…). Only Cursor adds `variables` for `MODELLIX_API_KEY`.
- Edit `.plugin/plugin.json` first, then mirror. `homepage` = https://docs.modellix.ai/ways-to-use/plugin
- `openclaw.plugin.json`: `skills: ["./skills"]`, empty `configSchema`. Do **not** add `openclaw.extensions` unless intentionally shipping a native OpenClaw code plugin.
- `package.json`: keep `pi-package` keyword and `"pi": { "skills": ["./skills"] }`.
- Hermes metadata: `skills/modellix/SKILL.md` frontmatter (`metadata.hermes`, `required_environment_variables`).
- Never put credentials in manifests.

## Default models

When the user does not name a model (keep `SKILL.md` + examples + evals in sync):

| Task | Default slug |
|------|----------------|
| T2I | `google/nano-banana-2-lite` |
| T2V | `bytedance/seedance-2.0-mini-t2v` |
| I2I | `google/nano-banana-2-lite-edit` |
| I2V | `bytedance/seedance-2.0-fast-i2v` |
| V2V | `bytedance/seedance-2.0-fast-v2v` |

Verify via OpenAPI / `model describe`. Changing defaults → bump version everywhere + update evals.

## Update checklist

**CLI changed:** Diff npm/`--help` → `cli-playbook.md` + `SKILL.md`; update capability-matrix + scripts; paid submit = no blind retry (use `task history`); document `--allow-private-network` for CDN/proxy DNS quirks.

**Defaults/routing changed:** `SKILL.md` → examples/README/evals → bump all versions (patch docs, minor workflow, major breaking).

**REST/schema:** Prefer Docs MCP when connected, else live `llms.txt` / `docs_url`; touch `rest-playbook.md` only for shared REST semantics.

**Before finish:**

- [ ] No secrets in files or examples
- [ ] Manifests + versions in sync; valid JSON
- [ ] README install/credential sections match `SKILL.md`
- [ ] `python3 -m py_compile skills/modellix/scripts/*.py`
- [ ] `python3 skills/modellix/scripts/clean_build_artifacts.py`

## Smoke checks

```bash
# Manifests
python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('.*-plugin/*.json') + ['.plugin/plugin.json', '.agents/plugins/marketplace.json', 'openclaw.plugin.json', 'package.json', 'skills/modellix/skill.json']]"

# Host load (optional)
claude plugin validate .
claude --plugin-dir .
ln -s "$PWD" ~/.cursor/plugins/local/modellix   # then Reload Window
codex plugin marketplace add "$PWD"

# CLI (needs key + balance)
modellix-cli doctor --json
modellix-cli model run --model-slug google/nano-banana-2-lite --body '{"prompt":"smoke test"}' --wait --timeout 5m --json
# modellix-cli task download <task_id> --output-dir ./tmp-out --json --allow-private-network

python3 skills/modellix/scripts/preflight.py --json
```

`skills/modellix/evals/evals.json` is the regression reference; keep run artifacts out of the repo.

## Code style and security

- Markdown: imperative, explain non-obvious *why*; avoid ALL-CAPS spam.
- Python: stdlib, cross-platform; fail via stderr + non-zero exit.
- JSON: two-space indent, trailing newline.
- Examples: prefer `--json`; redact keys as `<MODELLIX_API_KEY>`.
- Never commit credentials / `.env` / keyed profiles. Session-only credentials by default.
- Egress: `api.modellix.ai`, `file.modellix.ai`, `docs.modellix.ai`.

## CI / publish

On `main` push, [`.github/workflows/skill_update.yml`](.github/workflows/skill_update.yml):

1. Smithery skill `modellix/modellix-skill` → git URL `skills/modellix/` (`SMITHERY_TOKEN`; slug kept for existing installs)
2. `npx skills add https://github.com/Modellix/modellix-plugin --skill modellix`
3. ClawHub skill `modellix/modellix` via inline `clawhub` CLI (`CLAWHUB_TOKEN`); accepts `published` / `pending-publication` / `submitted` / `unchanged`; retries on version collision; skips when `skills/` unchanged
4. ClawHub bundle-plugin `@modellix/modellix-plugin` only when `package.json` version changed (or `workflow_dispatch` + `force_publish`)

Merging to `main` publishes; do not trigger publish by hand. Claude/Codex marketplaces read the repo directly.

```bash
npx clawhub@latest package validate .
npx clawhub@latest package publish . --family bundle-plugin --owner modellix --dry-run --json
```

## Commits and PRs

English only. Prefer focused commits:

- `feat(plugin): …` / `feat(skill): …` / `fix(…): …` / `docs: …` / `chore: bump version to x.y.z`

Bump versions when behavior or packaged content changes.

## Common gotchas

- Trust npm CLI / `--help` over website CLI docs.
- Filename ≠ model slug (`seedance-2-0-…md` vs `bytedance/seedance-2.0-…`).
- Do not auto-retry ambiguous paid `model run` outcomes.
- Skill-only path is `skills/modellix`, not the repo root.
- Version must match across Open Plugins manifests + `skill.json` + `package.json` (+ Claude marketplace `metadata.version`).

## Quick file map

| Change | Touch first |
|--------|-------------|
| Plugin metadata / logo | `.plugin/plugin.json` → vendor manifests |
| Docs MCP endpoint | `.mcp.json` (keep URL in sync with https://docs.modellix.ai/mcp) |
| Always-on guardrails | `rules/*.mdc` (keep in sync with skill defaults / paid-submit / credential policy) |
| Marketplace | `.agents/plugins/marketplace.json`, `.claude-plugin/marketplace.json` |
| Defaults | `SKILL.md`, examples, `evals/evals.json`, version bump |
| CLI / REST | `SKILL.md`, `references/*`, scripts |
| Install copy | `README.md`, manifests, `skill.json` |
| Pi / Hermes | `package.json` + `.pi` symlink; SKILL.md Hermes frontmatter |
| External directory listings | `.cursor/hooks/community-listings.json` (+ sync script); see below |

## External directory listings

After `git push` to `main`, project Cursor hooks (`.cursor/hooks.json`) run a community listing check and may follow up on stop. Config and playbook live in:

- [`.cursor/hooks/community-listings.json`](.cursor/hooks/community-listings.json) — canonical URLs + targets
- [`.cursor/hooks/sync_community_listings.py`](.cursor/hooks/sync_community_listings.py) — `--check` / `--apply`

```bash
python3 .cursor/hooks/sync_community_listings.py --check
```

Do not invent listing targets in this file; edit the JSON. Official marketplaces (`manual_channels`) stay human-submitted. Awesome Copilot is `issue_form` — never PR `plugins/external.json` directly.
