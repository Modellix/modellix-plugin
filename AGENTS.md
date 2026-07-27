# AGENTS.md

Agent instructions for maintaining and updating the **Modellix plugin** in this repository.

Human-facing overview lives in [README.md](README.md). This file is for coding agents working on the plugin package itself.

## Project overview

This repo publishes the Modellix plugin consumed by AI coding agents (Cursor, Claude Code, Codex, ClawHub, Smithery, etc.). It follows the [Open Plugins specification](https://open-plugins.com/plugin-builders/specification): **the repository root is the plugin root**.

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
| [`.github/workflows/skill_update.yml`](.github/workflows/skill_update.yml) | On `main` push: sync Smithery + `npx skills add` |

There is no application runtime, package.json, or test suite for a product app. The “product” is the plugin manifests + skill markdown + scripts.

Because `skills/` is an Open Plugins default discovery path, the manifests deliberately omit a `skills` field. Do not add one unless the skill moves.

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

Install URLs:

```text
# Plugin (Claude Code / Codex marketplace)
Modellix/modellix-plugin

# Skill-only install
https://github.com/Modellix/modellix-plugin/tree/main/skills/modellix
```

## Manifest rules

- The four `plugin.json` files must stay in sync for shared metadata (`name`, `version`, `description`, `author`, `homepage`, `repository`, `license`, `logo`, `keywords`). Only the Cursor manifest carries the extra `variables` block.
- `.plugin/plugin.json` is the primary source; edit it first, then mirror.
- `name` must satisfy the spec: lowercase alphanumerics, hyphens, periods; no `--` or `..`.
- Keep `version` identical across the manifests and [`skills/modellix/skill.json`](skills/modellix/skill.json).
- Manifest directories must contain only `plugin.json` (and, for Claude, `marketplace.json`). Components live at the plugin root.
- Never put credentials in a manifest; the Cursor `variables` block only declares the variable name.

## Default models policy

When the end user does not name a model, the skill must use these defaults (update the table in `SKILL.md` and keep examples/evals in sync):

| Task | Default slug |
|------|----------------|
| T2I | `google/nano-banana-2-lite` |
| T2V | `bytedance/seedance-2.0-mini-t2v` |
| I2I | `bytedance/seedream-5.0-lite-edit` |
| I2V | `bytedance/seedance-2.0-fast-i2v` |
| V2V | `bytedance/seedance-2.0-v2v` |

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
2. After 60s, runs `npx skills add https://github.com/Modellix/modellix-plugin/tree/main/skills/modellix`.

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
- Version lives in five files (four manifests + `skill.json`); bump them together.

## Quick file map for edits

| Change type | Touch first |
|-------------|-------------|
| Plugin metadata / logo / keywords | `.plugin/plugin.json` then mirror to the three vendor manifests |
| Marketplace listing | `.agents/plugins/marketplace.json`, `.claude-plugin/marketplace.json` |
| Default models | `skills/modellix/SKILL.md`, examples, `skills/modellix/evals/evals.json`, version bump |
| CLI workflow | `skills/modellix/SKILL.md`, `skills/modellix/references/cli-playbook.md`, `capability-matrix.md`, scripts |
| REST fallback | `skills/modellix/references/rest-playbook.md`, `capability-matrix.md` |
| Install / registry copy | root `README.md`, manifests, `skills/modellix/skill.json` |
| Eval prompts | `skills/modellix/evals/evals.json` |

## Listing the plugin in external directories (PRs)

After meaningful updates land on `main`, optionally refresh or open listing PRs in community “awesome skills / plugins” repos. All PR titles/bodies and commits for those repos must be **English**.

### Canonical links (keep consistent)

| Purpose | URL |
|---------|-----|
| Skill package (install / PR source) | `https://github.com/Modellix/modellix-plugin/tree/main/skills/modellix` |
| Repo root / human README | `https://github.com/Modellix/modellix-plugin` |
| Plugin marketplace source | `Modellix/modellix-plugin` |
| ClawHub listing | `https://clawhub.ai/modellix/modellix` |
| Docs index | `https://docs.modellix.ai/llms.txt` |
| CLI package | `https://www.npmjs.com/package/modellix-cli` |

Suggested short description (≤10 words where required):

```text
Unified API for AI image and video generation
```

### Preconditions

1. Push the updated plugin to `origin/main` first (listings must point at a public tip).
2. Authenticate GitHub CLI (`gh auth login` or `GH_TOKEN` / git credential with `repo` scope).
3. Prefer a dedicated workdir outside this repo (e.g. `~/Developer/modellix-plugin-prs/`). Large awesome repos often fail full clones — use **sparse / shallow** clones or the **Contents API** (see sickn33 below).
4. Branch name convention: `add-modellix-skill`.
5. Fork under the submitting GitHub user, push the branch, open PR with `--head <user>:add-modellix-skill`.

Shared sparse-prep pattern:

```bash
export GH_TOKEN=... # or rely on gh auth
WORKDIR=~/Developer/modellix-plugin-prs
mkdir -p "$WORKDIR" && cd "$WORKDIR"

prep() {
 local upstream="$1" dir="$2" fork_repo="$3" # fork_repo = name under your user
 shift 3
 gh repo fork "$upstream" --clone=false --default-branch-only || true
 local default_branch
 default_branch=$(gh repo view "$upstream" --json defaultBranchRef -q .defaultBranchRef.name)
 rm -rf "$dir"
 git clone --filter=blob:none --sparse --depth 1 --single-branch \
 --branch "$default_branch" "https://github.com/$upstream.git" "$dir"
 cd "$dir"
 git sparse-checkout set --no-cone "$@"
 git remote rename origin upstream
 git remote add origin "https://github.com/<YOUR_USER>/${fork_repo}.git"
 git checkout -b add-modellix-skill
 cd ..
}
```

Retry `git push` / `gh pr create` on HTTP/2 EOF (use `GIT_HTTP_VERSION=HTTP/1.1` if needed).

### Target repos and how to contribute

#### 1) [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)

- **Type**: link-only curated list (skill stays in this repo).
- **Where**: Community Skills → Development and Testing (or a future “Skills by Modellix” official section if maintainers prefer).
- **Entry format**:

```markdown
- **[Modellix/modellix](https://github.com/Modellix/modellix-plugin/tree/main/skills/modellix)** - Unified API for AI image and video generation
```

- **Rules**: description ≤10 words; public repo + SKILL.md; they may reject brand-new / unused skills.
- **PR title**: `Add skill: Modellix/modellix`
- **Edit**: `README.md` only (append near end of the chosen community subsection).
- **Example PR**: https://github.com/VoltAgent/awesome-agent-skills/pull/801

#### 2) [VoltAgent/awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills)

- **Type**: ClawHub link list only.
- **Requirement**: skill must already be published on [ClawHub](https://clawhub.ai/modellix/modellix) with clean security status. Do **not** use `clawskills.sh` URLs in the PR (CONTRIBUTING forbids them); use `https://clawhub.ai/modellix/modellix`.
- **Where**: Image & Video Generation.
- **Entry format**:

```markdown
- [modellix](https://clawhub.ai/modellix/modellix) - Unified API for AI image and video generation.
```

- **Edit**:
 1. `README.md` — Image & Video Generation `<details>` block (before the “View all …” link).
 2. `categories/image-and-video-generation.md` — insert alphabetically (e.g. after `moonfunsdk`).
- **PR title**: `Add skill: modellix/modellix`
- **PR body**: include the ClawHub URL.
- **Example PR**: https://github.com/VoltAgent/awesome-openclaw-skills/pull/536

#### 3) [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)

- **Type**: README link (optional local `skill-name/SKILL.md` folder; external GitHub link is accepted).
- **Where**: Creative & Media, alphabetical by display name.
- **Entry format**:

```markdown
- [Modellix](https://github.com/Modellix/modellix-plugin/tree/main/skills/modellix) - Generate images and videos via Modellix's unified model API and CLI. *By [Modellix](https://modellix.ai)*
```

- **PR title**: `Add Modellix skill`
- **PR body**: problem solved, audience, source URL, short usage example (per their CONTRIBUTING).
- **Edit**: `README.md` under `### Creative & Media`.
- **Example PR**: https://github.com/ComposioHQ/awesome-claude-skills/pull/1355

#### 4) [sickn33/agentic-awesome-skills](https://github.com/sickn33/agentic-awesome-skills)

- **Type**: vendored `skills/<name>/SKILL.md` in their repo (catalog is auto-generated — **do not** edit `CATALOG.md` / `data/*.json`).
- **Where**: add only `skills/modellix/SKILL.md`.
- **Frontmatter** (folder name must match `name`):

```yaml
---
name: modellix
description: "Integrate Modellix unified API/CLI for async AI image and video generation (model run --wait, task download)."
category: creative
risk: safe
source: community
source_repo: Modellix/modellix-plugin
source_type: official
date_added: "YYYY-MM-DD"
author: Modellix
tags: [image-generation, video-generation, modellix, cli, api]
tools: [claude, cursor, gemini]
license: "MIT"
license_source: "https://github.com/Modellix/modellix-plugin/blob/main/LICENSE"
---
```

Body: short Overview / When to Use / How It Works / Examples pointing at the upstream package (keep lean; full instructions live upstream).

- **Validate** (if clone works): `npm install && npm run validate`
- **PR title**: `feat: add modellix for AI image and video generation`
- **API fallback** when clone fails (create branch + file on the fork, then PR):

```bash
DEFAULT=$(gh repo view sickn33/agentic-awesome-skills --json defaultBranchRef -q .defaultBranchRef.name)
BASE_SHA=$(gh api repos/sickn33/agentic-awesome-skills/git/ref/heads/$DEFAULT --jq .object.sha)
gh api --method POST repos/<YOUR_USER>/agentic-awesome-skills/git/refs \
 -f ref=refs/heads/add-modellix-skill -f sha="$BASE_SHA"
# PUT skills/modellix/SKILL.md with base64 content on branch add-modellix-skill
gh api --method PUT repos/<YOUR_USER>/agentic-awesome-skills/contents/skills/modellix/SKILL.md \
 -f message='feat: add modellix for AI image and video generation' \
 -f content="$(base64 < SKILL.md | tr -d '\n')" \
 -f branch=add-modellix-skill
gh pr create --repo sickn33/agentic-awesome-skills \
 --head '<YOUR_USER>:add-modellix-skill' \
 --title 'feat: add modellix for AI image and video generation' \
 --body '...'
```

- **Example PR**: https://github.com/sickn33/agentic-awesome-skills/pull/867

#### 5) [anthropics/skills](https://github.com/anthropics/skills)

- **Not a community skill dump.** Do **not** add folders under `./skills/`.
- Optional ask: add a **Partner Skills** README bullet (same style as Notion), link only:

```markdown
- **Modellix** - [Modellix Skill for AI image and video generation](https://github.com/Modellix/modellix-plugin/tree/main/skills/modellix)
```

- **PR title**: `Add Modellix to Partner Skills`
- Expect curation; maintainers may decline. Sparse-checkout carefully — only stage `README.md` (avoid deleting unchecked files like `THIRD_PARTY_NOTICES.md`).
- **Example PR**: https://github.com/anthropics/skills/pull/1445

#### 6) [Qoder-AI/qoder-community](https://github.com/Qoder-AI/qoder-community)

- **Type**: Astro content collection (listing + localized body), not a vendored full skill tree.
- **Guide**: [CONTRIBUTING.md](https://github.com/Qoder-AI/qoder-community/blob/main/CONTRIBUTING.md)
- **Where**:
 1. English: `src/content/skills/modellix.md` (full frontmatter + body)
 2. Chinese: `src/content/skills-zh/modellix.md` (frontmatter is only `slug: modellix`; body in Chinese)
- **Category**: `design` (image/video generation). Other allowed values: `development | design | marketing | productivity | automation | data | security | document | meta`.
- **Sparse paths**: `src/content/skills` `src/content/skills-zh` (optional: `CONTRIBUTING.md`).
- **English frontmatter pattern**:

```yaml
---
name: modellix
title: Modellix
description: Generate images and videos via Modellix's unified model API and CLI (model run --wait, task download).
source: community
author: Modellix
githubUrl: https://github.com/Modellix/modellix-plugin/tree/main/skills/modellix
docsUrl: https://docs.modellix.ai/llms.txt
category: design
tags:
 - image-generation
 - video-generation
 - modellix
 - cli
 - api
roles:
 - designer
 - developer
 - marketer
featured: false
popular: false
isOfficial: false
installCommand: |
 git clone https://github.com/Modellix/modellix-plugin
 cp -r modellix-plugin/skills/modellix ~/.qoder/skills/modellix
 npm i -g modellix-cli@latest
date: YYYY-MM-DD
lastUpdated: YYYY-MM-DD
---
```

- **Chinese file** starts with:

```yaml
---
slug: modellix
---
```

- **Body sections** (match existing skills): Use Cases / Core Capabilities / Example / Notes (EN); 使用场景 / 核心能力 / 示例 / 注意事项 (ZH).
- **Install note**: copy only `skills/modellix/` into `~/.qoder/skills/modellix`, then install `modellix-cli`.
- **PR title**: `Add Modellix skill for AI image and video generation`
- **PR body**: link the package URL; mention EN + ZH files; note content-only change.
- **Example PR**: https://github.com/Qoder-AI/qoder-community/pull/79

### Plugin-specific directories

| Channel | Entry | Notes |
|---------|-------|-------|
| [cursor.directory](https://cursor.directory/plugins/new) | Paste the repo URL | Auto-detects the Open Plugins layout |
| [Cursor Marketplace](https://cursor.com/marketplace/publish) | Manual review | Requires public + open-source repo; re-reviewed on updates |
| [Claude plugin directory](https://platform.claude.com/plugins/submit) | Manual review | Run `claude plugin validate .` first |
| [Codex plugins](https://developers.openai.com/codex/submit-plugins) | Manual review | Needs listing copy plus 5 positive / 3 negative test cases |

### Update vs first submit

| Situation | Action |
|-----------|--------|
| First time | Open PRs as above (skip any already merged). |
| Repo renamed / install URL changed | Open follow-up PRs updating the same README / `SKILL.md` lines in every merged listing. |
| ClawHub slug/author changed | Update openclaw entry + canonical links table together. |
| Already merged, no listing text change | No directory PR needed; `main` push + Smithery workflow is enough. |

### After opening PRs

- Record URLs in the PR conversation with the maintainer (Chinese chat OK).
- Watch CI on sickn33 (`skill-review` / validate).
- If VoltAgent asks for “community usage”, point at ClawHub installs / Smithery / public repo activity.
