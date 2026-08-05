# Modellix Plugin

Agent plugin for [Modellix](https://modellix.ai), a unified Model-as-a-Service (MaaS) platform for image, video, and audio workflows.

This repository follows the [Open Plugins](https://open-plugins.com/plugin-builders/specification) specification: the repository root **is** the plugin root, and the skill ships as `skills/modellix/`. The same layout installs into Cursor, Claude Code, Codex, OpenClaw, OpenCode, Pi, Hermes, and any Agent Skills host.

Official install guide: [docs.modellix.ai/ways-to-use/plugin](https://docs.modellix.ai/ways-to-use/plugin).

## What this plugin provides

- CLI-first workflow: `modellix-cli doctor` → `model run --wait` → `task download`
- REST fallback when the CLI is unavailable
- Default models when the user does not specify one
- Model discovery via `modellix-cli model list` / `model describe`, plus live docs at [llms.txt](https://docs.modellix.ai/llms.txt)
- Optional **Docs MCP** (`.mcp.json` → [docs.modellix.ai/mcp](https://docs.modellix.ai/mcp)) for searching and reading official documentation — not for running generation tasks
- Slash **commands** under `commands/`: `/modellix:image`, `/modellix:video`, `/modellix:audio`, `/modellix:doctor`, `/modellix:models`, `/modellix:tasks`, `/modellix:download`
- Persistent **rules** under `rules/` (Open Plugins `.mdc`): CLI-first defaults, paid-submit safety, credential/docs guardrails
- Optional **hooks** under `hooks/`: confirm before a repeated paid submit or an unbounded `model batch`, and remind the agent to download results before they expire
- Retry and error guidance aligned with CLI exit codes and paid-submit safety
- Credential handling for `MODELLIX_API_KEY` and CLI auth profiles

## Requirements

- A Modellix API key from the [Console](https://modellix.ai/console/api-key)
- Recommended: [modellix-cli](https://www.npmjs.com/package/modellix-cli) (Node.js 18.17+)
- Optional hooks: Python 3.9+; a cross-platform Node launcher finds `py`, `python`, or `python3` and fails open when Python is unavailable

```bash
npm i -g modellix-cli@latest
modellix-cli doctor --json
```

## Install and update

After install, use an existing authenticated CLI profile or set `MODELLIX_API_KEY` (see [Setup](#setup)).

Prefer **Plugin** when the host supports Open Plugins / marketplace plugins. Use **Skill** when you only need the Agent Skill (`skills/modellix`), or when the host has no plugin marketplace.

### 1) Plugin

Installs the repository root as a plugin (manifests + `skills/modellix/`).

#### Claude Code

Install:

```text
/plugin marketplace add Modellix/modellix-plugin
/plugin install modellix@modellix
```

Update:

```text
/plugin marketplace update modellix
/plugin update modellix@modellix
```

Or use the `/plugin` UI, then `/reload-plugins` if needed.

Local development:

```bash
claude --plugin-dir /path/to/modellix-plugin
claude plugin validate /path/to/modellix-plugin
```

#### Codex

Install:

```bash
codex plugin marketplace add Modellix/modellix-plugin
# then install modellix from /plugins
```

Update: re-open `/plugins` and update, or re-add the marketplace and reinstall.

#### Cursor

Official Marketplace (after approval):

```text
/add-plugin modellix
```

GitHub or local checkout: open **Customize → Plugins → + Add**, choose this repository, then install **Modellix** from the `modellix` marketplace declared in `.cursor-plugin/marketplace.json`.

For symlink-based development:

```bash
git clone https://github.com/Modellix/modellix-plugin.git
ln -sfn "$PWD/modellix-plugin" ~/.cursor/plugins/local/modellix
# Developer: Reload Window — confirm under Customize
```

Update:

```bash
git -C ~/.cursor/plugins/local/modellix pull   # when the symlink points at a clone
# Developer: Reload Window
```

#### OpenClaw (bundle plugin)

ClawHub package `@modellix/modellix-plugin` — Open Plugins layout as a content/skill bundle (not a TypeScript runtime plugin).

Install:

```bash
openclaw plugins install clawhub:@modellix/modellix-plugin

# local / git
openclaw plugins install .
openclaw plugins install git:github.com/Modellix/modellix-plugin
```

Update: reinstall from the same ClawHub/git/path source (or `git pull` if you linked a local checkout). `openclaw plugins update` only refreshes npm-tracked installs.

#### Pi (package)

[Pi](https://github.com/badlogic/pi-mono) loads this repo as a [Pi package](https://docs.pi.dev/packages) (skills only — not an Open Plugins marketplace plugin). `package.json` declares `pi-package` and `pi.skills`; the repo also exposes `.pi/skills/modellix` → `skills/modellix` for local discovery.

Install:

```bash
pi install git:github.com/Modellix/modellix-plugin
# or
pi install https://github.com/Modellix/modellix-plugin
# local checkout
pi install /path/to/modellix-plugin
```

Update:

```bash
pi update --extensions
# or pin/move ref:
pi install git:github.com/Modellix/modellix-plugin
```

---

### 2) Skill

Installs only `skills/modellix` (Agent Skill). Useful for skills.sh, ClawHub skills, OpenCode, Pi, Hermes, Smithery, or Cursor skill-only installs.

#### Agent Skills (skills.sh) — any host

Install:

```bash
npx skills add https://github.com/Modellix/modellix-plugin --skill modellix
npx skills add https://github.com/Modellix/modellix-plugin --skill modellix --agent cursor   # one agent
```

Update:

```bash
npx skills update
```

#### ClawHub / OpenClaw (skill)

Slug `modellix` (skill registry; separate from the `@modellix/modellix-plugin` package above).

Install:

```bash
clawhub install modellix
# or
openclaw skills install modellix
```

Update:

```bash
clawhub update modellix
# or
clawhub update --all
```

#### OpenCode

OpenCode’s [plugins](https://opencode.ai/docs/zh-cn/plugins/) are JS/TS event hooks — Modellix does **not** use that path. Use [Agent Skills](https://opencode.ai/docs/skills/) instead. This repo exposes `.opencode/skills/modellix` → `skills/modellix`.

Install:

```bash
npx skills add https://github.com/Modellix/modellix-plugin --skill modellix

# Global
mkdir -p ~/.config/opencode/skills
ln -sfn /path/to/modellix-plugin/skills/modellix ~/.config/opencode/skills/modellix

# Project-local
mkdir -p .opencode/skills
ln -sfn /path/to/modellix-plugin/skills/modellix .opencode/skills/modellix
```

Update:

```bash
npx skills update
# or, for a symlink install:
git -C /path/to/modellix-plugin pull
```

In OpenCode, load with `skill({ name: "modellix" })`.

#### Cursor (skill-only)

When you want the skill without installing the full Cursor plugin:

```bash
npx skills add https://github.com/Modellix/modellix-plugin --skill modellix --agent cursor
npx skills update
```

#### Smithery

Install:

```bash
npx @smithery/cli@latest skill add modellix/modellix-skill
npx @smithery/cli@latest skill add modellix/modellix-skill --agent cursor
```

Update: re-run the same `skill add` command (or your Smithery client’s update flow).

#### Pi (skill-only)

Prefer the [Pi package](#pi-package) install above. Skill-only alternatives:

```bash
npx skills add https://github.com/Modellix/modellix-plugin --skill modellix
# Pi also scans ~/.agents/skills/

# or symlink the skill tree
mkdir -p ~/.pi/agent/skills
ln -sfn /path/to/modellix-plugin/skills/modellix ~/.pi/agent/skills/modellix
```

#### Hermes Agent

[Hermes](https://hermes-agent.nousresearch.com/) uses Agent Skills (`SKILL.md`), not Open Plugins. Short listing blurb: **Unified API for AI image, video, and audio workflows**.

Install:

```bash
hermes skills install Modellix/modellix-plugin/skills/modellix
# or from skills.sh (when listed):
# hermes skills install skills-sh/Modellix/modellix-plugin/modellix

# copy / symlink into the Hermes skills tree
mkdir -p ~/.hermes/skills
ln -sfn /path/to/modellix-plugin/skills/modellix ~/.hermes/skills/modellix
```

To reuse a shared Agent Skills directory, add under `skills` in `~/.hermes/config.yaml`:

```yaml
skills:
  external_dirs:
    - ~/.agents/skills
```

Update: re-run `hermes skills install ...`, or `git pull` on a symlink checkout. After install, start a new session and invoke `/modellix` (or load the skill via Hermes skill tools). Set `MODELLIX_API_KEY` in the environment or `~/.hermes/.env` (Hermes may prompt securely on first load when the skill declares `required_environment_variables`).

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
- In Hermes, prefer `~/.hermes/.env` or the secure prompt when the skill loads (`required_environment_variables`).
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
| Text-to-speech (TTS) | `alibaba/qwen-audio-3.0-tts-flash` |
| Speech-to-text (STT) | `openai/whisper-1` |
| Speech-to-speech (STS) | `alibaba/cosyvoice-clone` |

To discover or inspect other models:

```bash
modellix-cli model list --type text-to-image --output slugs
modellix-cli model describe <provider/model> --json
```

Request-body schemas come from each model’s docs (prefer the plugin Docs MCP when connected; otherwise `docs_url` from `model describe`, or links in [llms.txt](https://docs.modellix.ai/llms.txt)).

## Execution guidance

1. Prefer CLI when installed; otherwise use REST ([API guide](https://docs.modellix.ai/ways-to-use/api.md)).
2. Do not hand-roll `task get` polling loops when `model run --wait` or `task wait` is available.
3. Do not blindly retry a paid `model run` after an unknown submission outcome — check `modellix-cli task history` first.
4. Optional helpers in `skills/modellix/scripts/` wrap CLI/REST; if they fail, call the CLI commands directly.
5. CLI behavior source of truth: [npm modellix-cli](https://www.npmjs.com/package/modellix-cli) and `modellix-cli --help` (not the website CLI guide page, which may lag).

## Security and data handling

Prompts and public media inputs are sent to `https://api.modellix.ai` only when a documented generation, editing, transcription, or speech task is invoked. The Docs MCP is read-only and connects only to `https://docs.modellix.ai/mcp`; it does not receive the API key or submit tasks. Spend-safety hook state contains hashes, model slugs, task ids, and timestamps, never prompts, request bodies, complete commands, or keys. See [SECURITY.md](SECURITY.md) and the [Modellix Privacy Policy](https://www.modellix.ai/privacy).

## Hooks (spend and result safety)

Hosts that support Open Plugins hooks load three lightweight guards. They only react to `modellix-cli` commands and never change the CLI workflow itself:

| Hook | Trigger | Behavior |
| --- | --- | --- |
| Run guard | Before a `model run` / `model invoke` / `model batch` shell command | Asks for confirmation when the same paid submit repeats in a session or when `model batch` has no `--max-tasks`; suggests `doctor` when no credential is discoverable |
| Task watch | After a `modellix-cli` command | Records task ids from the output and clears them once `task download` succeeds |
| Stop reminder | When the agent tries to finish | Sends one follow-up if tasks were generated but never downloaded (resource URLs expire in about 7 days) |

Config lives in [`hooks/hooks.json`](hooks/hooks.json) (Open Plugins / Claude Code event names) and [`hooks/cursor-hooks.json`](hooks/cursor-hooks.json) (Cursor event names); each manifest points at exactly one of them, so a host never runs both. Hook logic is Python 3 stdlib only, while `scripts/run_python_hook.mjs` selects the available Python 3 command across platforms. Per-session state stores command fingerprints, model slugs, and task ids—never prompts or keys—and every hook fails open. Hosts without hook support (Pi, Hermes, OpenCode, Codex) ignore this directory.

Plugin-level `scripts/` holds these hook scripts; the CLI/REST helpers used by the skill live in `skills/modellix/scripts/`.

## Slash commands

Hosts that support Open Plugins commands expose seven shortcuts. Each one routes to the same `modellix-cli` workflow the skill teaches—they add no separate runtime:

| Command | Use it for |
| --- | --- |
| `/modellix:image [prompt] [image url]` | Text-to-image, or image editing when input images are given |
| `/modellix:video [prompt] [image or video url]` | Text-to-video, image-to-video, or video-to-video |
| `/modellix:audio [tts\|stt\|sts] [text or audio url]` | Text-to-speech, speech-to-text, or speech-to-speech |
| `/modellix:doctor [profile]` | CLI install, credential resolution, connectivity, balance |
| `/modellix:models [term or slug]` | Find a model and its request-body schema |
| `/modellix:tasks [task id]` | Task status, plus recovery after a timeout or unknown submission |
| `/modellix:download [task id] [dir]` | Fetch results into `./outputs` before the ~7-day expiry |

The three paid commands (`image`, `video`, `audio`) set `disable-model-invocation: true`, so only a human can trigger them; the read-only four can also be called by the agent. Hosts without command support (Pi, Hermes, OpenCode, the ClawHub skill bundle) ignore [`commands/`](commands/) and keep using the skill.

## Supported task types

| Type | Description |
| --- | --- |
| `text-to-image` | Generate images from text prompts |
| `image-to-image` | Edit or transform images with text instructions |
| `text-to-video` | Create videos from text descriptions |
| `image-to-video` | Convert static images into video sequences |
| `video-to-video` | Transform existing videos |
| `text-to-speech` | Synthesize speech from text |
| `speech-to-text` | Transcribe public audio resources |
| `speech-to-speech` | Clone or transform a voice from reference audio |

## Repository structure

```text
.
├── README.md                       # This file (humans)
├── SECURITY.md                     # Credential, network, local-state, and disclosure policy
├── AGENTS.md                       # Maintainer / coding-agent instructions
├── CHANGELOG.md
├── package.json                    # ClawHub OpenClaw + Pi package (@modellix/modellix-plugin)
├── openclaw.plugin.json            # OpenClaw package manifest (skills bundle)
├── .mcp.json                       # Docs MCP → https://docs.modellix.ai/mcp (read-only docs search)
├── commands/                       # Slash commands (:image, :video, :audio, :doctor, :models, :tasks, :download)
├── rules/                          # Open Plugins always-on guardrails (.mdc)
├── hooks/                          # Hook configs: hooks.json (Open Plugins/Claude), cursor-hooks.json (Cursor)
├── scripts/                        # Hook logic (Python stdlib) + cross-platform Node launcher
├── .opencode/skills/modellix       # Symlink → skills/modellix (OpenCode skill discovery)
├── .pi/skills/modellix             # Symlink → skills/modellix (Pi local skill discovery)
├── .plugin/plugin.json             # Vendor-neutral Open Plugins manifest
├── .cursor-plugin/
│   ├── plugin.json                 # Cursor manifest (+ optional MODELLIX_API_KEY variable)
│   └── marketplace.json            # Single-repository Cursor marketplace entry
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json            # Claude Code marketplace entry
├── .codex-plugin/plugin.json
├── .agents/plugins/marketplace.json # Codex / vendor-neutral marketplace entry
├── assets/logo.svg
├── tests/                           # Repository and paid-safety regression tests (not packaged)
├── skills/
│   └── modellix/                   # Skill package (SKILL.md, scripts, references, assets, evals)
└── .github/workflows/              # Publish sync (Smithery / skills add / ClawHub)
```

`skills/modellix/` sits on the Open Plugins default discovery path, so no `skills` field is needed in the Open Plugins manifests. Pi uses `package.json#pi.skills`; Hermes installs the skill tree only (no Hermes-specific plugin manifest).

## Maintaining this plugin

See [AGENTS.md](AGENTS.md) for sources of truth, update checklists, smoke tests, versioning, and PR conventions.

Current version: see [`.plugin/plugin.json`](.plugin/plugin.json) (kept in sync with [`skills/modellix/skill.json`](skills/modellix/skill.json)).

## Links

- Product: [modellix.ai](https://modellix.ai)
- Docs: [docs.modellix.ai](https://docs.modellix.ai)
- Models index: [llms.txt](https://docs.modellix.ai/llms.txt)
- Plugin guide: [ways-to-use/plugin](https://docs.modellix.ai/ways-to-use/plugin)
- Agent skill guide: [ways-to-use/skill](https://docs.modellix.ai/ways-to-use/skill.md)
- Docs MCP: [ways-to-use/mcp](https://docs.modellix.ai/ways-to-use/mcp) ([endpoint](https://docs.modellix.ai/mcp))
- REST API: [ways-to-use/api](https://docs.modellix.ai/ways-to-use/api.md)
- CLI package: [npmjs.com/package/modellix-cli](https://www.npmjs.com/package/modellix-cli)
- Pricing: [get-started/pricing](https://docs.modellix.ai/get-started/pricing)
- Support: [support@modellix.ai](mailto:support@modellix.ai)
- Community: [Discord](https://discord.gg/N2FbcB2cZT)
