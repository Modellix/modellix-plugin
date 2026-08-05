# AGENTS.md

Instructions for coding agents that maintain this **Modellix plugin** package. Human install and product overview live in [README.md](README.md).

## Project overview

This repository is an [Open Plugins](https://open-plugins.com/plugin-builders/specification) **v1** plugin: **the git repository root is the plugin root**. It ships one Agent Skill at `skills/modellix/` for Modellix image, video, and audio workflows (CLI-first, REST fallback), a read-only **Docs MCP** at `.mcp.json`, always-on **rules**, spend-safety **hooks**, and seven slash **commands**. Hosts that consume it include Cursor, Claude Code, Codex, OpenClaw/ClawHub, OpenCode, Pi, Hermes, and any Agent Skills host.

There is no application runtime or unit-test suite. The product is manifests + skill markdown + thin Python helpers.

```text
modellix-plugin/                 ← plugin root (= repo root)
├── .plugin/plugin.json          ← vendor-neutral Open Plugins manifest (edit first)
├── .cursor-plugin/              ← Cursor plugin.json + single-repo marketplace.json
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
├── commands/                    ← slash commands (thin prompts routing to the CLI flow)
├── rules/                       ← Open Plugins always-on .mdc guardrails
├── hooks/                       ← hooks.json (Open Plugins/Claude) + cursor-hooks.json (Cursor)
├── scripts/                     ← plugin-level hook scripts + cross-platform Node launcher
├── package.json                 ← ClawHub + Pi (`pi-package`, pi.skills)
├── .opencode/skills/modellix → ../../skills/modellix
├── .pi/skills/modellix → ../../skills/modellix
└── .github/workflows/skill_update.yml
```

## Open Plugins conformance

Follow https://open-plugins.com/plugin-builders/specification (and marketplace/install docs on the same site). Rules that matter here:

1. **Plugin root = repo root.** All component paths are relative to that root and use `./…`. Never `../` outside the plugin tree.
2. **Manifests:** Prefer `.plugin/plugin.json` as the source of truth; keep vendor copies (`.cursor-plugin/`, `.claude-plugin/`, `.codex-plugin/`) in sync for shared metadata. Each metadata directory contains **only** `plugin.json`, except Claude and Cursor, which may also carry their host-specific `marketplace.json`. Components live at the plugin root, not inside `.plugin/`.
3. **Default discovery:** Hosts load `skills/` automatically. Because the skill lives at `skills/modellix/`, Open Plugins manifests **omit** a `skills` field — do not add one unless the skill moves off the default path.
4. **Do not invent unused components.** Never create top-level `agents/` or `.lsp.json` unless you intend to ship them (hosts auto-discover those paths). This plugin ships `.mcp.json` (Docs MCP), `rules/*.mdc` (always-on guardrails), `hooks/` + `scripts/` (spend-safety hooks), and `commands/*.md` (slash commands). Do not ship repository-level `.cursor/hooks.json` or unrelated stop follow-ups: the repo root is the install artifact, so maintainer automation would affect every installer and fail marketplace security review.
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
9. **Cursor plugin schema / review reference:** https://github.com/cursor/plugins (`schemas/plugin.schema.json`, `schemas/marketplace.schema.json`, and `create-plugin/skills/review-plugin-submission/SKILL.md`)

Skill workflow to teach:

```text
doctor → (defaults or model list/describe) → model run --wait → task download
```

`model invoke` is only a compatibility alias of `model run`.

## Language

- **English** for all repo artifacts (manifests, SKILL.md, playbooks, scripts, commits, PR text, and marketplace copy).
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

## Commands

Seven markdown prompts in `commands/`; the filename is the command name, hosts namespace it as `/modellix:<file>`.

| File | Paid | Role |
|------|------|------|
| `image.md` | yes | T2I, or I2I when the request carries input images |
| `video.md` | yes | T2V / I2V / V2V routed by input type |
| `audio.md` | yes | TTS / STT / STS routed by the requested speech workflow |
| `doctor.md` | no | `--version` + `doctor --json`, credential lifecycle pointer |
| `models.md` | no | `model list` filters, `model describe`, schema lookup |
| `tasks.md` | no | `task history` / `get` / `wait`, unknown-submit recovery |
| `download.md` | no | `task download`, private-network fallback, expiry warning |

Invariants when editing commands:

- **Thin prompts, not policy.** A command routes arguments to an existing CLI flow and points at `skills/modellix/SKILL.md`. Do not restate the credential lifecycle, retry table, or REST fallback — that duplication goes stale.
- **Paid commands stay user-only.** `image.md`, `video.md`, and `audio.md` set `disable-model-invocation: true` so an agent cannot spend by calling a command; agent-initiated generation goes through the skill, where the rules and hooks apply.
- **Frontmatter is the union of hosts.** `description` (all hosts), `argument-hint` (Claude), `disable-model-invocation` (spec + Claude). Unknown keys are ignored elsewhere. Only `$ARGUMENTS` is a guaranteed placeholder — never `$1` / `$2`.
- **Handle empty arguments.** Ask the user instead of inventing a prompt or a task id.
- Default slugs appearing in `image.md` / `video.md` / `audio.md` must match the Default models table below, `SKILL.md`, and [`rules/cli-and-defaults.mdc`](rules/cli-and-defaults.mdc).

`commands/` is a default Open Plugins discovery path, so vendor-neutral manifests may omit a `commands` field; the Cursor manifest declares it explicitly for official-schema clarity. ClawHub installs the skill bundle only and will not expose these commands—that is expected.

## Hooks

Two configs, one behavior. Cursor uses camelCase flat entries; Open Plugins/Claude Code use PascalCase nested actions, so a single file cannot serve both. Each manifest points at exactly one config (a manifest `hooks` path replaces default `hooks/hooks.json` discovery), which keeps a host from firing both.

| File | Consumed by | Events |
|------|-------------|--------|
| [`hooks/hooks.json`](hooks/hooks.json) | `.plugin`, `.claude-plugin` | `PreToolUse` / `PostToolUse` (matcher `Bash`), `Stop`; `${PLUGIN_ROOT}` |
| [`hooks/cursor-hooks.json`](hooks/cursor-hooks.json) | `.cursor-plugin` | `beforeShellExecution` / `afterShellExecution` (matcher `modellix-cli`), `stop` with `loop_limit: 1`; `${CURSOR_PLUGIN_ROOT}` |

Scripts in `scripts/` (plugin level; the skill's CLI wrappers stay in `skills/modellix/scripts/`):

| Script | Role |
|--------|------|
| `_hook_lib.py` | Payload normalization (Cursor vs Claude shapes), host-aware responses, session state, redaction |
| `run_python_hook.mjs` | Cross-platform launcher that selects `py -3`, `python`, or `python3` and fails open when Python is unavailable |
| `modellix_run_guard.py` | `ask` on repeated paid submits and on `model batch` without `--max-tasks`; `doctor` hint when no credential is discoverable |
| `modellix_task_watch.py` | Records task ids, clears them after a successful `task download` |
| `modellix_stop_reminder.py` | One follow-up when tasks were never downloaded |

Invariants when editing hooks:

- **Fail open.** Any unexpected input, parse error, or missing state emits `{}` and exits 0. Never exit 2 (that means deny) from these scripts.
- **Only decide when flagging.** Emit `{}` for the normal path. Never return `allow` on the Claude/Open Plugins side — `permissionDecision: "allow"` bypasses that host's permission system; advisory text goes through `systemMessage` (`lib.advise()`).
- **Modellix-only.** Bail out unless the command matches `modellix-cli`; Claude matchers only filter by tool, so re-check in the script.
- **No secrets, no prompts on disk.** Session state under the temp dir stores command fingerprints, slugs, and task ids only; never persist the original command or request body, and keep files at mode `600`.
- **No second runtime.** Hooks warn and confirm; they must not submit, poll, or download on their own. Execution policy stays in `SKILL.md` / `rules/`.
- Keep the ask/reminder wording aligned with `SKILL.md` Error / Retry Policy and [`rules/paid-submit-safety.mdc`](rules/paid-submit-safety.mdc).

## Manifest rules

- Keep shared metadata in sync across the four Open Plugins `plugin.json` files, `skills/modellix/skill.json`, and root `package.json` (`name`/`version`/`description`/`homepage`/…). Cursor also adds `displayName`, `publisher`, discovery metadata, explicit component paths, and an optional `MODELLIX_API_KEY` variable; `.cursor-plugin/marketplace.json` must resolve back to the repository root.
- Edit `.plugin/plugin.json` first, then mirror. `homepage` = https://docs.modellix.ai/ways-to-use/plugin
- `openclaw.plugin.json`: `skills: ["./skills"]`, empty `configSchema`. Do **not** add `openclaw.extensions` or hooks there — ClawHub treats this as a content bundle.
- Hook wiring: `.cursor-plugin` → `./hooks/cursor-hooks.json`; `.plugin` and `.claude-plugin` → `./hooks/hooks.json`; `.codex-plugin` stays without hooks.
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
| TTS | `alibaba/qwen-audio-3.0-tts-flash` |
| STT | `openai/whisper-1` |
| STS | `alibaba/cosyvoice-clone` |

Verify via OpenAPI / `model describe`. Changing defaults → bump version everywhere + update evals.

## Update checklist

**CLI changed:** Diff npm/`--help` → `cli-playbook.md` + `SKILL.md`; update capability-matrix + scripts; paid submit = no blind retry (use `task history`); document `--allow-private-network` for CDN/proxy DNS quirks.

**Defaults/routing changed:** `SKILL.md` → examples/README/evals → bump all versions (patch docs, minor workflow, major breaking).

**REST/schema:** Prefer Docs MCP when connected, else live `llms.txt` / `docs_url`; touch `rest-playbook.md` only for shared REST semantics.

**Before finish:**

- [ ] No secrets in files or examples
- [ ] Manifests + versions in sync; valid JSON
- [ ] README install/credential sections match `SKILL.md`
- [ ] `npm test` (cross-platform Python 3 launcher)
- [ ] `python -m py_compile scripts/*.py skills/modellix/scripts/*.py`
- [ ] `python skills/modellix/scripts/clean_build_artifacts.py`

## Smoke checks

```bash
# Manifests
python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('.*-plugin/*.json') + glob.glob('hooks/*.json') + ['.plugin/plugin.json', '.agents/plugins/marketplace.json', 'openclaw.plugin.json', 'package.json', 'skills/modellix/skill.json', '.mcp.json']]"

# Commands (frontmatter present + default slugs consistent)
python3 -c "import pathlib,sys; [sys.exit(f'bad frontmatter: {p}') for p in sorted(pathlib.Path('commands').glob('*.md')) if not (p.read_text().startswith('---') and 'description:' in p.read_text().split('---')[1])]"
rg -n 'nano-banana-2-lite|seedance-2\.0' commands/

# Hooks (stdin payloads; expect {} for non-Modellix, ask on a repeated paid submit)
echo '{"command":"ls -la"}' | python3 scripts/modellix_run_guard.py
echo '{"tool_name":"Bash","tool_input":{"command":"modellix-cli model batch tasks.jsonl"}}' | python3 scripts/modellix_run_guard.py

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
| Plugin metadata / logo | `.plugin/plugin.json` → vendor manifests; Cursor-only listing fields in `.cursor-plugin/` |
| Docs MCP endpoint | `.mcp.json` (keep URL in sync with https://docs.modellix.ai/mcp) |
| Slash commands | `commands/*.md` (thin prompts; keep default slugs in sync with `SKILL.md`) |
| Always-on guardrails | `rules/*.mdc` (keep in sync with skill defaults / paid-submit / credential policy) |
| Hook behavior | `scripts/*.py`, `scripts/run_python_hook.mjs`, and both `hooks/*.json` (keep the two configs equivalent) |
| Marketplace | `.cursor-plugin/`, `.agents/plugins/marketplace.json`, `.claude-plugin/marketplace.json` |
| Defaults | `SKILL.md`, examples, `evals/evals.json`, version bump |
| CLI / REST | `SKILL.md`, `references/*`, scripts |
| Install copy | `README.md`, manifests, `skill.json` |
| Pi / Hermes | `package.json` + `.pi` symlink; SKILL.md Hermes frontmatter |
| Cursor Marketplace | Validate `.cursor-plugin/plugin.json` and `marketplace.json` against the current `cursor/plugins` schemas before submission |
