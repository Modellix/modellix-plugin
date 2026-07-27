# Modellix Plugin

Agent plugin for [Modellix](https://modellix.ai), a unified Model-as-a-Service (MaaS) platform for image and video generation.

This repository follows the [Open Plugins](https://open-plugins.com/plugin-builders/specification) specification: the repository root **is** the plugin root, and the skill ships as `skills/modellix/`. The same layout installs into Cursor, Claude Code, Codex, and any Agent Skills host.

## What this plugin provides

- CLI-first workflow: `modellix-cli doctor` → `model run --wait` → `task download`
- REST fallback when the CLI is unavailable
- Default models when the user does not specify one
- Model discovery via `modellix-cli model list` / `model describe`, plus live docs at [llms.txt](https://docs.modellix.ai/llms.txt)
- Retry and error guidance aligned with CLI exit codes and paid-submit safety
- Credential handling for `MODELLIX_API_KEY` and CLI auth profiles

## Requirements

- A Modellix API key from the [Console](https://modellix.ai/console/api-key)
- Recommended: [modellix-cli](https://www.npmjs.com/package/modellix-cli) (Node.js 18.17+)

```bash
npm i -g modellix-cli@latest
modellix-cli doctor --json
```

## Install

### Claude Code

```text
/plugin marketplace add Modellix/modellix-plugin
/plugin install modellix@modellix
```

### Codex

```bash
codex plugin marketplace add Modellix/modellix-plugin
# then install modellix from /plugins
```

### Cursor

Browse or submit via [cursor.directory](https://cursor.directory/plugins/new), or link the repository for local use:

```bash
git clone https://github.com/Modellix/modellix-plugin.git
ln -s "$PWD/modellix-plugin" ~/.cursor/plugins/local/modellix
# then run "Developer: Reload Window" and confirm the skill under Customize
```

### Agent Skills (skills.sh)

The skill can still be installed on its own, without the plugin wrapper:

```bash
npx skills add https://github.com/Modellix/modellix-plugin/tree/main/skills/modellix
```

Cursor:

```bash
npx skills add https://github.com/Modellix/modellix-plugin/tree/main/skills/modellix --agent cursor
```

Update installed skills:

```bash
npx skills update
```

### From Smithery

```bash
npx @smithery/cli@latest skill add modellix/modellix-skill
```

### From ClawHub

```bash
clawhub install modellix
clawhub update --all
```

## Setup

| Item | Value |
| --- | --- |
| Primary credential / env | `MODELLIX_API_KEY` |
| Console | https://modellix.ai/console/api-key |

```bash
export MODELLIX_API_KEY="your_api_key"
```

- REST requires `MODELLIX_API_KEY`.
- CLI may use the env var **or** a saved profile (`modellix-cli auth login` / `init`).
- In Cursor, the key can also be set as the `MODELLIX_API_KEY` plugin variable.
- Prefer session-only keys; persist only when you explicitly ask for it.
- Never commit API keys or print them in logs.

Key resolution order in the CLI: `--api-key` → `MODELLIX_API_KEY` → selected saved profile.

## Quick start (CLI)

```bash
modellix-cli doctor --json

modellix-cli model run \
  --model-slug google/nano-banana-2-lite \
  --body '{"prompt":"A cinematic sunset over a futuristic city skyline"}' \
  --wait --timeout 5m --json

modellix-cli task download <task_id> --output-dir ./outputs --json
```

If `task download` fails with a private/reserved network error (common behind local proxies that map CDN hosts into `198.18.0.0/15`), retry with `--allow-private-network` for trusted Modellix CDN hosts, or download the resource URL with `curl`.

`model invoke` remains a compatibility alias of `model run`. Prefer `model run` in new scripts.

## Default models

Used when the user does **not** name a model:

| Task type | Default model slug |
| --- | --- |
| Text-to-image (T2I) | `google/nano-banana-2-lite` |
| Text-to-video (T2V) | `bytedance/seedance-2.0-mini-t2v` |
| Image editing / I2I | `google/nano-banana-2-lite-edit` |
| Image-to-video / I2V | `bytedance/seedance-2.0-fast-i2v` |
| Video-to-video (V2V) | `bytedance/seedance-2.0-fast-v2v` |

To discover or inspect other models:

```bash
modellix-cli model list --type text-to-image --output slugs
modellix-cli model describe <provider/model> --json
```

Request-body schemas come from each model’s docs (`docs_url` from `model describe`, or links in [llms.txt](https://docs.modellix.ai/llms.txt)).

## Execution guidance

1. Prefer CLI when installed; otherwise use REST ([API guide](https://docs.modellix.ai/ways-to-use/api.md)).
2. Do not hand-roll `task get` polling loops when `model run --wait` or `task wait` is available.
3. Do not blindly retry a paid `model run` after an unknown submission outcome — check `modellix-cli task history` first.
4. Optional helpers in `skills/modellix/scripts/` wrap CLI/REST; if they fail, call the CLI commands directly.
5. CLI behavior source of truth: [npm modellix-cli](https://www.npmjs.com/package/modellix-cli) and `modellix-cli --help` (not the website CLI guide page, which may lag).

## Supported task types

| Type | Description |
| --- | --- |
| `text-to-image` | Generate images from text prompts |
| `image-to-image` | Edit or transform images with text instructions |
| `text-to-video` | Create videos from text descriptions |
| `image-to-video` | Convert static images into video sequences |
| `video-to-video` | Transform existing videos |

## Repository structure

```text
.
├── README.md                       # This file (humans)
├── AGENTS.md                       # Maintainer / coding-agent instructions
├── CHANGELOG.md
├── .plugin/plugin.json             # Vendor-neutral manifest (primary source)
├── .cursor-plugin/plugin.json      # Cursor manifest (+ MODELLIX_API_KEY variable)
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json            # Claude Code marketplace entry
├── .codex-plugin/plugin.json
├── .agents/plugins/marketplace.json # Codex / vendor-neutral marketplace entry
├── assets/logo.svg
├── skills/
│   └── modellix/                   # Skill package (SKILL.md, scripts, references, assets, evals)
└── .github/workflows/              # Publish sync (Smithery / skills add)
```

`skills/modellix/` sits on the Open Plugins default discovery path, so no `skills` field is needed in the manifests.

## Maintaining this plugin

See [AGENTS.md](AGENTS.md) for sources of truth, update checklists, smoke tests, versioning, and PR conventions.

Current version: see [`.plugin/plugin.json`](.plugin/plugin.json) (kept in sync with [`skills/modellix/skill.json`](skills/modellix/skill.json)).

## Links

- Product: [modellix.ai](https://modellix.ai)
- Docs: [docs.modellix.ai](https://docs.modellix.ai)
- Models index: [llms.txt](https://docs.modellix.ai/llms.txt)
- Agent skill guide: [ways-to-use/skill](https://docs.modellix.ai/ways-to-use/skill.md)
- REST API: [ways-to-use/api](https://docs.modellix.ai/ways-to-use/api.md)
- CLI package: [npmjs.com/package/modellix-cli](https://www.npmjs.com/package/modellix-cli)
- Pricing: [get-started/pricing](https://docs.modellix.ai/get-started/pricing)
- Support: [support@modellix.ai](mailto:support@modellix.ai)
- Community: [Discord](https://discord.gg/N2FbcB2cZT)
