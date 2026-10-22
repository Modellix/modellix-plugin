# AGENTS.md

Instructions for coding agents that maintain this **Modellix plugin** package. Human install and product overview live in [README.md](README.md).

## Project overview

This repository conforms to [Agent Plugins](https://agent-plugins.org/specification) **1.0.0**: **the git repository root is the plugin root**, root `plugin.json` is the portable manifest, immediate children under `skills/` are portable Agent Skills, and root `mcp.json` declares **Modellix Docs Search**, **Modellix Media Generation**, and **Modellix Web Tools**. Cursor, Claude Code, Codex, legacy Open Plugins, OpenClaw/ClawHub, OpenCode, Pi, and Hermes adapters add host capabilities such as rules, hooks, and fourteen slash commands without changing the portable core.

There is no application runtime. The product is manifests + skill markdown + thin stdlib Python helpers, covered by repository regression tests.

```text
modellix-plugin/                 ← plugin root (= repo root)
├── plugin.json                  ← Agent Plugins 1.0.0 portable manifest (edit first)
├── mcp.json                     ← Agent Plugins MCP servers (streamable-http; no auth headers)
├── .plugin/plugin.json          ← legacy Open Plugins host adapter
├── .cursor-plugin/              ← Cursor plugin.json + single-repo marketplace.json
├── .claude-plugin/              ← Claude Code plugin.json + marketplace.json
├── .codex-plugin/plugin.json
├── .agents/plugins/marketplace.json
├── assets/logo.svg
├── skills/modellix-design/             ← execution skill (Media Generation MCP / CLI / REST)
│   ├── SKILL.md
│   ├── skill.json
│   ├── references/              ← media MCP / cli / rest / capability playbooks
│   ├── scripts/                 ← CLI update/preflight + execution helpers (stdlib Python)
│   ├── assets/
│   └── evals/
├── skills/modellix-image-prompt-engineering/ ← prompt-only image planning skill
│   ├── SKILL.md
│   ├── skill.json
│   ├── references/              ← prompt / concepts / failure / grid playbooks
│   └── evals/
├── skills/modellix-ffmpeg/             ← local edit / concat / transcode skill
│   ├── SKILL.md
│   ├── skill.json
│   ├── references/              ← concat and edit recipes
│   ├── scripts/                 ← install check only; never installs FFmpeg
│   └── evals/
├── skills/modellix-moviepy/            ← local composite / titles / timeline skill
│   ├── SKILL.md
│   ├── skill.json
│   ├── references/              ← text overlay and timeline
│   ├── scripts/                 ← install check only; never installs moviepy
│   └── evals/
├── skills/modellix-social-card/        ← prompt-only social card planning skill
│   ├── SKILL.md
│   ├── skill.json
│   ├── references/              ← platform ratios and card planning
│   └── evals/
├── skills/modellix-infographic/        ← prompt-only infographic planning skill
│   ├── SKILL.md
│   ├── skill.json
│   ├── references/              ← information structures and prompt shape
│   └── evals/
├── skills/modellix-ecomm-ugc-video/    ← prompt-only ecommerce UGC video planning skill
│   ├── SKILL.md
│   ├── skill.json
│   ├── references/              ← UGC patterns and shot prompts
│   └── evals/
├── skills/modellix-cover-image/        ← prompt-only article cover planning skill
│   ├── SKILL.md
│   ├── skill.json
│   ├── references/              ← cover type, palette, rendering, and prompt shape
│   └── evals/
├── skills/modellix-comic/              ← prompt-only knowledge comic planning skill
│   ├── SKILL.md
│   ├── skill.json
│   ├── references/              ← style, preset, and storyboard
│   └── evals/
├── skills/modellix-article-illustrator/ ← prompt-only in-article illustration planning skill
│   ├── SKILL.md
│   ├── skill.json
│   ├── references/              ← type, style, preset, and prompt shape
│   └── evals/
├── openclaw.plugin.json         ← ClawHub bundle-plugin (skills only; no extensions)
├── .mcp.json                    ← Cursor/legacy MCP adapter (`type: http`; same servers, no auth headers)
├── commands/                    ← slash commands (thin prompts; each routes to one skill)
├── rules/                       ← host-specific always-on .mdc guardrails
├── hooks/                       ← hooks.json (legacy/Claude) + cursor-hooks.json (Cursor)
├── scripts/                     ← plugin-level hook scripts + cross-platform Node launcher
├── package.json                 ← npm + ClawHub + Pi (`bin`, `pi-package`, pi.skills)
├── .opencode/skills/modellix-design → ../../skills/modellix-design
├── .opencode/skills/modellix-image-prompt-engineering → ../../skills/modellix-image-prompt-engineering
├── .opencode/skills/modellix-ffmpeg → ../../skills/modellix-ffmpeg
├── .opencode/skills/modellix-moviepy → ../../skills/modellix-moviepy
├── .opencode/skills/modellix-social-card → ../../skills/modellix-social-card
├── .opencode/skills/modellix-infographic → ../../skills/modellix-infographic
├── .opencode/skills/modellix-ecomm-ugc-video → ../../skills/modellix-ecomm-ugc-video
├── .opencode/skills/modellix-cover-image → ../../skills/modellix-cover-image
├── .opencode/skills/modellix-comic → ../../skills/modellix-comic
├── .opencode/skills/modellix-article-illustrator → ../../skills/modellix-article-illustrator
├── .pi/skills/modellix-design → ../../skills/modellix-design
├── .pi/skills/modellix-image-prompt-engineering → ../../skills/modellix-image-prompt-engineering
├── .pi/skills/modellix-ffmpeg → ../../skills/modellix-ffmpeg
├── .pi/skills/modellix-moviepy → ../../skills/modellix-moviepy
├── .pi/skills/modellix-social-card → ../../skills/modellix-social-card
├── .pi/skills/modellix-infographic → ../../skills/modellix-infographic
├── .pi/skills/modellix-ecomm-ugc-video → ../../skills/modellix-ecomm-ugc-video
├── .pi/skills/modellix-cover-image → ../../skills/modellix-cover-image
├── .pi/skills/modellix-comic → ../../skills/modellix-comic
├── .pi/skills/modellix-article-illustrator → ../../skills/modellix-article-illustrator
└── .github/workflows/skill_update.yml
```

## Agent Plugins 1.0.0 core and host adapters

Follow https://agent-plugins.org/specification for the portable core. Rules that matter here:

1. **Plugin root = repo root.** All component paths are relative to that root and use `./…`. Never `../` outside the plugin tree.
2. **Portable manifest:** Root `plugin.json` is the source of truth and uses the exact 1.0.0 `$schema`. Its schema is closed; client-specific data must not be added as arbitrary top-level fields. Mirror shared metadata into `.plugin/`, `.cursor-plugin/`, `.claude-plugin/`, `.codex-plugin/`, `skill.json`, and `package.json`.
3. **Fixed core discovery:** Agent Plugins 1.0.0 discovers only immediate skills under `skills/` and MCP servers from root `mcp.json`. The manifest does not declare paths. Keep root `mcp.json` on `streamable-http`; `.mcp.json` remains a separate Cursor/legacy adapter using its host's `http` spelling. Do not copy one file's `type` into the other: clients connect with the declared transport and do not fall back. Remote MCP headers must not contain secrets or `${...}` placeholders; this spec does not expand them.
4. **Host extensions stay layered.** Agent Plugins 1.0.0 core defines skills and MCP only. This repository additionally ships `.mcp.json`, `rules/*.mdc`, `hooks/` + `scripts/`, and `commands/*.md` for hosts that support them. Never move those fields into root `plugin.json`. Do not ship repository-level `.cursor/hooks.json` or unrelated stop follow-ups: the repo root is the install artifact, so maintainer automation would affect every installer and fail marketplace security review.
5. **Names:** `name` is lowercase alphanumerics, hyphens, periods; no `--` or `..`. Current name: `modellix`.
6. **`${PLUGIN_ROOT}`** (Claude also accepts `${CLAUDE_PLUGIN_ROOT}`) for paths that must resolve against the plugin root. Skill-internal refs stay relative to the skill root (`scripts/…`, `references/…`).
7. **Pi / Hermes** reuse the trees under `skills/` (Pi via `package.json#pi` / symlinks; Hermes via skill install + SKILL.md frontmatter). Do not invent Pi-/Hermes-only plugin manifest directories.

## Sources of truth

Do not invent CLI flags, model slugs, or install paths from memory:

1. **CLI:** [npm `modellix-cli`](https://www.npmjs.com/package/modellix-cli) + local `modellix-cli --help`
2. **REST:** https://docs.modellix.ai/ways-to-use/api.md
3. **Models:** `modellix-cli model get-schema <slug>` for request/response schema; `modellix-cli model describe <slug> --json` / https://docs.modellix.ai/llms.txt for catalog metadata and narrative docs
4. **Docs search:** Modellix Docs Search at https://docs.modellix.ai/mcp via portable [`mcp.json`](mcp.json) and host adapter [`.mcp.json`](.mcp.json). Documentation only; it does not receive the API key.
5. **Media generation MCP:** Modellix Media Generation at https://tool.modellix.ai/mcp/media, declared beside Docs Search with no `Authorization` header. The host attaches the key. Tool details live in `skills/modellix-design/references/media-mcp-playbook.md`.
6. **Web Tools MCP:** Modellix Web Tools at https://tool.modellix.ai/mcp, declared beside Docs Search and Media Generation with no `Authorization` header. The host attaches the key. Tools are `modellix-ai/web-search` and `modellix-ai/web-fetch`. Calls are billed. Docs: https://docs.modellix.ai/tools/mcp
7. **Plugin format:** https://agent-plugins.org/specification and the official `schemas/1.0.0/*.schema.json`
8. **Published install guide:** https://docs.modellix.ai/ways-to-use/plugin.md (flag drift vs README when install or routing changes)
9. Do **not** treat `docs.modellix.ai/ways-to-use/cli.md` as authoritative until it matches the npm CLI
10. Do **not** reintroduce `references/REFERENCE.md` mirroring `llms.txt`
11. **Cursor plugin schema / review reference:** https://github.com/cursor/plugins (`schemas/plugin.schema.json`, `schemas/marketplace.schema.json`, and `create-plugin/skills/review-plugin-submission/SKILL.md`)

Skill workflow to teach:

```text
Media Generation tools available and input is not a local file:
  user-named slug → modellix_get_schema → modellix_submit_task once → modellix_wait_task → save resources

Otherwise:
  user-named slug, or ask if none was named → model get-schema → model run --wait → task download
```

`model invoke` is only a compatibility alias of `model run`.

## Language

- **English** for all repo artifacts (manifests, SKILL.md, playbooks, scripts, commits, PR text, and marketplace copy).
- **Chinese** when chatting with the human maintainer.
- Do not translate existing English content unless asked.

## Setup

```bash
export MODELLIX_API_KEY="..."   # session only; never commit
python3 skills/modellix-design/scripts/preflight.py --json
python3 skills/modellix-design/scripts/clean_build_artifacts.py
```

Python helpers: stdlib only (no pip deps for `cli_runtime.py`, `preflight.py`, `invoke_and_poll.py`, `check_ffmpeg.py`, or `check_moviepy.py`). `preflight.py` must resolve/check public npm `latest` before the workflow's first CLI command; update failures retain a working CLI, never downgrade, and never retry a paid submit. `check_ffmpeg.py` only reports whether FFmpeg is usable and prints an install command; it never runs that command. `check_moviepy.py` does the same for moviepy 2.x and Pillow.

## Layout and skill rules

Progressive disclosure for the execution skill:

| Path | Role |
|------|------|
| `SKILL.md` | Policies and short examples; prefer staying under ~500 lines |
| `references/media-mcp-playbook.md` | Media Generation tools, used when the input is not a local file |
| `references/cli-playbook.md` | Full CLI surface |
| `references/rest-playbook.md` | REST only when Media Generation and the CLI are unavailable |
| `references/capability-matrix.md` | Media Generation ↔ CLI ↔ REST mapping |
| `scripts/` | CLI update/preflight + optional execution wrapper; must retain direct CLI/REST fallback |

Keep exactly ten immediate skill trees with separate responsibilities:

- `skills/modellix-image-prompt-engineering/` prepares T2I/I2I prompts and never executes, authenticates, submits, polls, or downloads.
- `skills/modellix-social-card/` plans mainstream social-card prompts and never executes, authenticates, submits, polls, or downloads.
- `skills/modellix-infographic/` plans one infographic prompt and never executes, authenticates, submits, polls, or downloads.
- `skills/modellix-ecomm-ugc-video/` plans vertical ecommerce UGC shot prompts and never executes, authenticates, submits, polls, or downloads.
- `skills/modellix-cover-image/` plans one article-cover prompt and never executes, authenticates, submits, polls, or downloads.
- `skills/modellix-comic/` plans a knowledge-comic storyboard and one prompt per page and never executes, authenticates, submits, polls, or downloads.
- `skills/modellix-article-illustrator/` plans one prompt per in-article illustration and never executes, authenticates, submits, polls, or downloads.
- `skills/modellix-design/` owns all Modellix execution policy, model schemas, credentials, paid-submit safety, waiting, and downloads.
- `skills/modellix-moviepy/` composites local files into a finished spot (titles, lower thirds, timed voiceover) and never calls Modellix, reads an API key, or installs moviepy without the user confirming the printed command.
- `skills/modellix-ffmpeg/` edits local files (concatenate, trim, reframe, transcode, subtitle-file burns) and never calls Modellix, reads an API key, or installs FFmpeg without the user confirming the printed command.

The matching `.opencode/skills/*` and `.pi/skills/*` entries are symlinks only — do not duplicate any of the trees. OpenCode’s JS/TS `.opencode/plugins/` system is unused here. Do not publish `modellix-ffmpeg`, `modellix-moviepy`, `modellix-social-card`, `modellix-infographic`, `modellix-ecomm-ugc-video`, `modellix-cover-image`, `modellix-comic`, or `modellix-article-illustrator` as their own Smithery or ClawHub skills; they ship inside the plugin package. A skill-only install of `modellix-design` does not include them.

## Commands

Fourteen markdown prompts in `commands/`; the filename is the command name, hosts namespace it as `/modellix:<file>`.

| File | Paid | Role |
|------|------|------|
| `prompt.md` | no | prepare an image prompt/brief without submitting |
| `social-card.md` | no | plan social-card prompts without submitting |
| `infographic.md` | no | plan one infographic prompt without submitting |
| `ecomm-ugc-video.md` | no | plan a vertical ecommerce UGC video without submitting |
| `cover-image.md` | no | plan one article-cover prompt without submitting |
| `comic.md` | no | plan a knowledge-comic storyboard without submitting |
| `article-illustrator.md` | no | plan in-article illustration prompts without submitting |
| `image.md` | yes | T2I, or I2I when the request carries input images |
| `video.md` | yes | T2V / I2V / V2V routed by input type |
| `audio.md` | yes | TTS / STT / STS routed by the requested speech workflow |
| `doctor.md` | no | `--version` + `doctor --json`, credential lifecycle pointer |
| `models.md` | no | `model list` filters, `model describe`, `model get-schema` |
| `tasks.md` | no | `task history` / `get` / `wait`, unknown-submit recovery |
| `download.md` | no | `task download`, private-network fallback, expiry warning |

Invariants when editing commands:

- **Thin prompts, not policy.** A command routes arguments to one skill: `prompt.md` points at `skills/modellix-image-prompt-engineering/SKILL.md`; `social-card.md` points at `skills/modellix-social-card/SKILL.md`; `infographic.md` points at `skills/modellix-infographic/SKILL.md`; `ecomm-ugc-video.md` points at `skills/modellix-ecomm-ugc-video/SKILL.md`; `cover-image.md` points at `skills/modellix-cover-image/SKILL.md`; `comic.md` points at `skills/modellix-comic/SKILL.md`; `article-illustrator.md` points at `skills/modellix-article-illustrator/SKILL.md`; execution commands point at `skills/modellix-design/SKILL.md`. Upstream planning skills hand completed briefs to the execution skill, but the execution skill does not enumerate or depend on its callers. Do not restate the credential lifecycle, retry table, or REST fallback — that duplication goes stale.
- **Paid commands stay user-only.** `image.md`, `video.md`, `audio.md`, `prompt.md`, `social-card.md`, `infographic.md`, `ecomm-ugc-video.md`, `cover-image.md`, `comic.md`, and `article-illustrator.md` set `disable-model-invocation: true`. An agent cannot spend by calling a paid command; agent-initiated generation goes through the skill, where the rules and hooks apply.
- **Frontmatter is the union of hosts.** `description` (all hosts), `argument-hint` (Claude), `disable-model-invocation` (spec + Claude). Unknown keys are ignored elsewhere. Only `$ARGUMENTS` is a guaranteed placeholder — never `$1` / `$2`.
- **Handle empty arguments.** Ask the user instead of inventing a prompt or a task id.
- Commands must not assign a model slug. If the user did not name one, the command asks. Keep that rule aligned with `SKILL.md` and [`rules/cli-and-defaults.mdc`](rules/cli-and-defaults.mdc).

`commands/` is a host-extension discovery path, not an Agent Plugins 1.0.0 core component. The Cursor manifest declares it explicitly; compatible legacy hosts may discover it by convention. ClawHub installs the skill bundle only and will not expose these commands—that is expected.

## Hooks

Two configs, one host-extension behavior. Cursor uses camelCase flat entries; legacy Open Plugins/Claude Code use PascalCase nested actions, so a single file cannot serve both. Agent Plugins 1.0.0 itself does not define hooks. Each host manifest points at exactly one config, which keeps a host from firing both.

| File | Consumed by | Events |
|------|-------------|--------|
| [`hooks/hooks.json`](hooks/hooks.json) | legacy `.plugin`, `.claude-plugin` | `PreToolUse` / `PostToolUse` (matcher `Bash`), `Stop`; `${PLUGIN_ROOT}` |
| [`hooks/cursor-hooks.json`](hooks/cursor-hooks.json) | `.cursor-plugin` | `beforeShellExecution` / `afterShellExecution` (matcher `modellix-cli`), `beforeMCPExecution` / `afterMCPExecution` (matcher `modellix_submit_task`), `stop` with `loop_limit: 1`; `${CURSOR_PLUGIN_ROOT}` |

Scripts in `scripts/` (plugin level; the skill's CLI wrappers stay in `skills/modellix-design/scripts/`):

| Script | Role |
|--------|------|
| `_hook_lib.py` | Payload normalization (Cursor vs Claude shapes), host-aware responses, session state, redaction |
| `run_python_hook.mjs` | Cross-platform launcher that selects `py -3`, `python`, or `python3` and fails open when Python is unavailable |
| `modellix_run_guard.py` | `ask` on repeated paid CLI submits, on a CLI submit whose slug was already sent through Media Generation, and on `model batch` without `--max-tasks`; `doctor` hint when no credential is discoverable |
| `modellix_mcp_guard.py` | Cursor only: `ask` before a repeated `modellix_submit_task` for a slug already submitted via MCP or CLI; records slug and task id after the call |
| `modellix_task_watch.py` | Records task ids, clears them after a successful `task download` |
| `modellix_stop_reminder.py` | One follow-up when tasks were never downloaded |

Invariants when editing hooks:

- **Fail open.** Any unexpected input, parse error, or missing state emits `{}` and exits 0. Never exit 2 (that means deny) from these scripts.
- **Only decide when flagging.** Emit `{}` for the normal path. Never return `allow` on the Claude/Open Plugins side — `permissionDecision: "allow"` bypasses that host's permission system; advisory text goes through `systemMessage` (`lib.advise()`).
- **Modellix-only.** Shell hooks bail out unless the command matches `modellix-cli`. The Cursor MCP guard bails out unless the tool is `modellix_submit_task`. Claude matchers only filter by tool, so re-check in the script. Legacy hooks stay on `Bash` because that host config cannot see MCP tool calls.
- **No secrets, no prompts on disk.** Session state under the temp dir stores command fingerprints, slugs, and task ids only; never persist the original command or request body, and keep files at mode `600`.
- **No second runtime.** Hooks warn and confirm; they must not submit, poll, or download on their own. Execution policy stays in `SKILL.md` / `rules/`.
- Keep the ask/reminder wording aligned with `SKILL.md` Error / Retry Policy and [`rules/paid-submit-safety.mdc`](rules/paid-submit-safety.mdc).

## Manifest rules

- Keep plugin release metadata in sync across root `plugin.json`, the four host `plugin.json` adapters, `skills/modellix-design/skill.json`, and root `package.json` (`name`/`version`/`description`/`homepage`/…). `modellix-image-prompt-engineering`, `modellix-social-card`, `modellix-infographic`, `modellix-ecomm-ugc-video`, `modellix-cover-image`, `modellix-comic`, `modellix-article-illustrator`, `modellix-ffmpeg`, and `modellix-moviepy` have independent skill versions. Cursor also adds `displayName`, `publisher`, discovery metadata, explicit component paths, and an optional `MODELLIX_API_KEY` variable; `.cursor-plugin/marketplace.json` must resolve back to the repository root.
- Edit root `plugin.json` first, then mirror. `homepage` = https://docs.modellix.ai/ways-to-use/plugin
- `openclaw.plugin.json`: `skills: ["./skills"]`, empty `configSchema`. Do **not** add `openclaw.extensions` or hooks there — ClawHub treats this as a content bundle.
- Hook wiring: `.cursor-plugin` → `./hooks/cursor-hooks.json`; `.plugin` and `.claude-plugin` → `./hooks/hooks.json`; `.codex-plugin` stays without hooks.
- `package.json`: keep the `modellix-plugin` installer bin, public npm `publishConfig`, `pi-package` keyword, and `"pi": { "skills": ["./skills"] }`.
- `scripts/install.mjs`: keep npm installs explicit and reversible. `--host cursor` copies the complete package to Cursor's documented local-plugin directory; `--host portable` requires a target. Existing destinations require `--force` and are moved to a timestamped backup. Never install into the filesystem root, home directory, or inside the package source.
- Agent Skills frontmatter: only standard top-level fields. Put string-only host/listing metadata under `metadata`; keep credential hints in `skill.json` and the skill body rather than non-standard top-level YAML fields.
- Never put credentials in manifests.

## Model selection

Do not set a default model. The user names the `provider/model` slug. If they omit it, ask before any paid submit. Keep `SKILL.md`, commands, and evals on that rule.

Verify a named slug via `model get-schema` / OpenAPI / `model describe`.

## Update checklist

**CLI changed:** Diff npm/`--help` → `cli-playbook.md` + `SKILL.md`; update capability-matrix + scripts; paid submit = no blind retry (use `task history`); document `--allow-private-network` for CDN/proxy DNS quirks.

**Routing changed:** `SKILL.md` → examples/README/evals → bump all versions (patch docs, minor workflow, major breaking).

**REST/schema:** Prefer `model get-schema` when CLI is available; else Docs MCP / live `llms.txt` / `docs_url`. Touch `rest-playbook.md` only for shared REST semantics.

**Before finish:**

- [ ] No secrets in files or examples
- [ ] Manifests + versions in sync; valid JSON
- [ ] README install/credential sections match `SKILL.md`
- [ ] `npm test` (cross-platform Python 3 launcher)
- [ ] `python -m py_compile scripts/*.py skills/modellix-design/scripts/*.py skills/modellix-ffmpeg/scripts/*.py skills/modellix-moviepy/scripts/*.py`
- [ ] `python skills/modellix-design/scripts/clean_build_artifacts.py`

## Smoke checks

```bash
# Manifests
python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('.*-plugin/*.json') + glob.glob('hooks/*.json') + ['plugin.json', 'mcp.json', '.plugin/plugin.json', '.agents/plugins/marketplace.json', 'openclaw.plugin.json', 'package.json', 'skills/modellix-design/skill.json', 'skills/modellix-image-prompt-engineering/skill.json', 'skills/modellix-social-card/skill.json', 'skills/modellix-infographic/skill.json', 'skills/modellix-ecomm-ugc-video/skill.json', 'skills/modellix-cover-image/skill.json', 'skills/modellix-comic/skill.json', 'skills/modellix-article-illustrator/skill.json', 'skills/modellix-ffmpeg/skill.json', 'skills/modellix-moviepy/skill.json', '.mcp.json']]"

# Commands (frontmatter present)
python3 -c "import pathlib,sys; [sys.exit(f'bad frontmatter: {p}') for p in sorted(pathlib.Path('commands').glob('*.md')) if not (p.read_text().startswith('---') and 'description:' in p.read_text().split('---')[1])]"

# Hooks (stdin payloads; expect {} for non-Modellix, ask on a repeated paid submit)
echo '{"command":"ls -la"}' | python3 scripts/modellix_run_guard.py
echo '{"tool_name":"Bash","tool_input":{"command":"modellix-cli model batch tasks.jsonl"}}' | python3 scripts/modellix_run_guard.py

# Host load (optional)
claude plugin validate .
claude --plugin-dir .
ln -s "$PWD" ~/.cursor/plugins/local/modellix   # then Reload Window
codex plugin marketplace add "$PWD"

# CLI (needs key + balance for a paid smoke; get-schema is public)
# Substitute a slug you choose. This plugin does not keep a default model.
modellix-cli doctor --json
modellix-cli model get-schema <provider/model>
modellix-cli model run --model-slug <provider/model> --body '{"prompt":"smoke test"}' --wait --timeout 5m --json
# modellix-cli task download <task_id> --output-dir ./tmp-out --json --allow-private-network

python3 skills/modellix-design/scripts/preflight.py --json

# npm installer (no host mutation in dry-run mode)
node scripts/install.mjs install --host cursor --dry-run
```

Each skill keeps its regression reference under `skills/<name>/evals/evals.json`; keep run artifacts out of the repo.

## Code style and security

- Markdown: imperative, explain non-obvious *why*; avoid ALL-CAPS spam.
- Python: stdlib, cross-platform; fail via stderr + non-zero exit.
- JSON: two-space indent, trailing newline.
- Examples: prefer `--json`; redact keys as `<MODELLIX_API_KEY>`.
- Never commit credentials / `.env` / keyed profiles. Session-only credentials by default.
- Egress: `api.modellix.ai`, `file.modellix.ai`, `tool.modellix.ai`, `docs.modellix.ai`.

## CI / publish

On `main` push, [`.github/workflows/skill_update.yml`](.github/workflows/skill_update.yml):

1. Smithery skill `modellix/modellix-skill` → git URL `skills/modellix-design/` (`SMITHERY_TOKEN`; slug kept for existing installs)
2. `npx skills add https://github.com/Modellix/modellix-plugin --skill modellix-design`
3. ClawHub skill `modellix/modellix-design` via inline `clawhub` CLI (`CLAWHUB_TOKEN`); accepts `published` / `pending-publication` / `submitted` / `unchanged`; retries on version collision; skips when `skills/modellix-design/` is unchanged
4. ClawHub bundle-plugin `@modellix/modellix-plugin` only when `package.json` version changed (or `workflow_dispatch` + `force_publish`)

Merging to `main` publishes the automated targets above; Claude/Codex marketplaces read the repo directly. npm is deliberately manual-only: publish `@modellix/modellix-plugin` from a trusted local environment using the single token stored outside the repository, after tests and `npm pack --dry-run`. Never add an npm token to GitHub Actions, workflow files, commits, or logs. Replace the local token when it expires or is rotated, and skip publishing when the exact version already exists.

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
- Skill-only execution path is `skills/modellix-design`; prompt-only image planning is `skills/modellix-image-prompt-engineering`; social-card prompts are `skills/modellix-social-card`; infographic prompts are `skills/modellix-infographic`; ecommerce UGC video plans are `skills/modellix-ecomm-ugc-video`; article covers are `skills/modellix-cover-image`; knowledge comics are `skills/modellix-comic`; in-article illustrations are `skills/modellix-article-illustrator`; local composites are `skills/modellix-moviepy`; local file edits are `skills/modellix-ffmpeg`. None of them uses the repo root as a skill path.
- The ClawHub bundle-plugin and npm package share `@modellix/modellix-plugin` as a name but are separate registries; always use an explicit `clawhub:` or `npm:` source with OpenClaw.
- Plain `npm install` materializes files but does not register every host. Only document direct npm consumption where the host supports it (currently Pi and OpenClaw); use `npx ... install --host cursor` for Cursor local installation.
- Plugin version must match across the root Agent Plugins manifest, the four host manifests, `package.json`, Claude marketplace `metadata.version`, `skills/modellix-design/skill.json`, and that skill's frontmatter. `modellix-image-prompt-engineering`, `modellix-social-card`, `modellix-infographic`, `modellix-ecomm-ugc-video`, `modellix-cover-image`, `modellix-comic`, `modellix-article-illustrator`, `modellix-ffmpeg`, and `modellix-moviepy` keep their own versions.

## Quick file map

| Change | Touch first |
|--------|-------------|
| Plugin metadata / logo | root `plugin.json` → host manifests; Cursor-only listing fields in `.cursor-plugin/` |
| Docs, Media Generation, and Web Tools MCP | root `mcp.json` (`streamable-http`) + `.mcp.json` host adapter (`http`); keep URLs in sync and leave headers empty |
| Slash commands | `commands/*.md` (thin prompts; do not invent a model slug) |
| Image prompt engineering | `skills/modellix-image-prompt-engineering/SKILL.md` + its `references/*`; keep execution out |
| Social card prompts | `skills/modellix-social-card/SKILL.md` + `references/*`; plan prompts only and hand generation to `modellix-design` |
| Infographic prompts | `skills/modellix-infographic/SKILL.md` + `references/*`; plan one prompt and never submit |
| Ecommerce UGC video | `skills/modellix-ecomm-ugc-video/SKILL.md` + `references/*`; plan shot prompts and hand each shot to `modellix-design` |
| Article covers | `skills/modellix-cover-image/SKILL.md` + `references/*`; plan one cover prompt and hand it to `modellix-design` |
| Knowledge comics | `skills/modellix-comic/SKILL.md` + `references/*`; plan one prompt per page and hand each page to `modellix-design` |
| Article illustrations | `skills/modellix-article-illustrator/SKILL.md` + `references/*`; plan one prompt per illustration and hand each image to `modellix-design` |
| Local FFmpeg edits | `skills/modellix-ffmpeg/SKILL.md` + `references/*` + `scripts/check_ffmpeg.py`; do not install FFmpeg without confirmation |
| Local moviepy composites | `skills/modellix-moviepy/SKILL.md` + `references/*` + `scripts/check_moviepy.py`; do not install moviepy without confirmation |
| Always-on guardrails | `rules/*.mdc` (keep in sync with model selection / paid-submit / credential policy) |
| Hook behavior | `scripts/*.py`, `scripts/run_python_hook.mjs`, and both `hooks/*.json` (shell guards stay aligned; Cursor also gates `modellix_submit_task`) |
| Marketplace | `.cursor-plugin/`, `.agents/plugins/marketplace.json`, `.claude-plugin/marketplace.json` |
| Defaults | Removed. The user names the slug in `SKILL.md`, commands, and `evals/evals.json` |
| CLI / REST | `SKILL.md`, `references/*`, scripts |
| Install copy / npm installer | `README.md`, `scripts/install.mjs`, `package.json`, manifests, `skill.json` |
| Pi / Hermes | `package.json` + `.pi` symlink; SKILL.md Hermes frontmatter |
| Cursor Marketplace | Validate `.cursor-plugin/plugin.json` and `marketplace.json` against the current `cursor/plugins` schemas before submission |
