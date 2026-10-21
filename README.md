# Modellix Plugin

Agent plugin for [Modellix](https://modellix.ai), a unified Model-as-a-Service (MaaS) platform for image, video, and audio workflows.

This repository conforms to the [Agent Plugins 1.0.0 specification](https://agent-plugins.org/specification): root [`plugin.json`](plugin.json) is the portable manifest, [`skills/`](skills/) is the fixed skill location, and root [`mcp.json`](mcp.json) declares Modellix Docs Search and Modellix Media Generation. Cursor, Claude Code, Codex, OpenClaw, OpenCode, Pi, and Hermes adapters remain alongside that core for hosts with additional or legacy capabilities.

Official install guide: [docs.modellix.ai/ways-to-use/plugin](https://docs.modellix.ai/ways-to-use/plugin).

## What this plugin provides

- Media Generation MCP when its tools are available and the input is not a local file; otherwise CLI: preflight → `modellix-cli doctor` → `model run --wait` → `task download`
- Image prompt engineering for covers, posters, mockups, edits, and coherent asset sets before execution
- Social card planning for mainstream network covers, thumbnails, and carousels. `skills/modellix-social-card/` writes one prompt per placement and does not generate images
- Infographic planning that turns a source into one prompt. `skills/modellix-infographic/` quotes the source facts and hands generation to `modellix-design`
- Local FFmpeg edits for files already on disk: concatenate, trim, reframe, transcode, and subtitle-file burns. `skills/modellix-ffmpeg/scripts/check_ffmpeg.py --json` only checks the install and prints the command; it does not install FFmpeg
- Local moviepy composites for files already on disk: titles, lower thirds, and a timed stack of clips and voiceover. `skills/modellix-moviepy/scripts/check_moviepy.py --json` only checks moviepy 2.x and Pillow; it does not install them
- Bounded server-side waits with resumable task IDs and no repeated paid submissions
- REST fallback when Media Generation and the CLI are both unavailable
- The user names the model. If they do not, ask which `provider/model` slug to run before submitting.
- Model discovery via `modellix_list_models` / `modellix_get_schema`, or `modellix-cli model list` / `model describe` / `model get-schema`, plus live docs at [llms.txt](https://docs.modellix.ai/llms.txt)
- **Modellix Docs Search** (`mcp.json`, plus host adapter `.mcp.json` → [docs.modellix.ai/mcp](https://docs.modellix.ai/mcp)) for searching and reading official documentation. It does not receive the API key and does not run generation
- **Modellix Media Generation** (same manifests → [tool.modellix.ai/mcp/media](https://tool.modellix.ai/mcp/media)) for image, video, and audio tasks. The host attaches the API key; the manifests do not contain it
- Slash **commands** under `commands/`: `/modellix:prompt`, `/modellix:social-card`, `/modellix:infographic`, `/modellix:image`, `/modellix:video`, `/modellix:audio`, `/modellix:doctor`, `/modellix:models`, `/modellix:tasks`, `/modellix:download`
- Persistent host **rules** under `rules/` (`.mdc`): Media Generation routing, paid-submit safety, credential/docs guardrails
- Optional **hooks** under `hooks/`: confirm before a repeated paid CLI submit or an unbounded `model batch`, confirm before a repeated `modellix_submit_task` on Cursor, and remind the agent to download results before they expire
- Retry and error guidance aligned with CLI exit codes and paid-submit safety
- Credential handling for `MODELLIX_API_KEY` and CLI auth profiles

## Requirements

- Prompt preparation needs no credential. Generation and authenticated API/CLI
  operations need a Modellix API key from the
  [Console](https://modellix.ai/console/api-key) or a saved CLI profile.
- [modellix-cli](https://www.npmjs.com/package/modellix-cli) 0.0.11+ requires Node.js 18.17+; the plugin preflight installs or refreshes it automatically from the public npm `latest` tag
- Python 3.10+ for automatic CLI preflight and optional hooks; direct CLI/REST use remains available when Python is unavailable
- FFmpeg (`ffmpeg` and `ffprobe`, with `libx264` and `aac`) only for local edits through `skills/modellix-ffmpeg/`. Generation does not need it. The check script prints an install command and does not install it.
- moviepy 2.x and Pillow only for local composites through `skills/modellix-moviepy/`. Generation does not need them. The check script prints `python3 -m pip install "moviepy>=2,<3" Pillow` and does not install them.

```bash
python3 skills/modellix-design/scripts/preflight.py --json
```

Preflight checks the installed version, upgrades only to a newer exact public npm version, then runs `doctor`. Registry/install failure keeps a working installed CLI; if no CLI is usable it recommends REST when `MODELLIX_API_KEY` is available. Set `MODELLIX_CLI_AUTO_UPDATE=0` only when an environment must pin its installed CLI.

## Install and update

After install, use an existing authenticated CLI profile or set `MODELLIX_API_KEY` (see [Setup](#setup)).

Prefer **Plugin** when the host supports Agent Plugins or marketplace plugins. Use
**Skill** when you only need execution (`skills/modellix-design`) or image prompt
engineering (`skills/modellix-image-prompt-engineering`), social card prompts
(`skills/modellix-social-card`), infographic prompts
(`skills/modellix-infographic`), or when the host has no
plugin marketplace.

### 1) Plugin

Installs the repository root as a plugin, including all six skills under `skills/`: `modellix-design`, `modellix-image-prompt-engineering`, `modellix-social-card`, `modellix-infographic`, `modellix-ffmpeg`, and `modellix-moviepy`.

#### npm / npx

The public npm package contains the complete portable plugin bundle. For Cursor, the installer copies it into Cursor's local-plugin directory:

```bash
npx --yes @modellix/modellix-plugin@latest install --host cursor

# update an existing npm-installed local plugin; the previous directory is kept as a backup
npx --yes @modellix/modellix-plugin@latest install --host cursor --force
```

For another Agent Plugins-compatible host, materialize a versioned bundle and point the host's local-plugin flow at that directory:

```bash
npx --yes @modellix/modellix-plugin@latest install --host portable --target ./modellix-plugin
```

Plain `npm install @modellix/modellix-plugin` only downloads the package into `node_modules`; it does not register the plugin with every host. Prefer the host-specific marketplace commands below when available. Pi and OpenClaw can consume the npm package directly through their own package installers.

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

ClawHub package `@modellix/modellix-plugin` — plugin content/skill bundle (not a TypeScript runtime plugin).

Install:

```bash
openclaw plugins install npm:@modellix/modellix-plugin

# or from ClawHub
openclaw plugins install clawhub:@modellix/modellix-plugin

# local / git
openclaw plugins install .
openclaw plugins install git:github.com/Modellix/modellix-plugin
```

Update npm installs with `openclaw plugins update npm:@modellix/modellix-plugin`. Reinstall from the same ClawHub/git/path source for other installs (or `git pull` if you linked a local checkout).

#### Pi (package)

[Pi](https://github.com/badlogic/pi-mono) loads this repo as a [Pi package](https://docs.pi.dev/packages) (skills only — not an Agent Plugins marketplace client). `package.json` declares `pi-package` and `pi.skills`; the repo also exposes four matching `.pi/skills/*` symlinks, one for each skill.

Install:

```bash
pi install npm:@modellix/modellix-plugin
# or
pi install git:github.com/Modellix/modellix-plugin
# or
pi install https://github.com/Modellix/modellix-plugin
# local checkout
pi install /path/to/modellix-plugin
```

Update:

```bash
pi update --extensions
# or update only the npm package:
pi update npm:@modellix/modellix-plugin
# or pin/move ref:
pi install git:github.com/Modellix/modellix-plugin
```

---

### 2) Skill

Install `modellix-design` or `modellix-image-prompt-engineering` on their own.
`modellix-design` executes image, video, and audio workflows and is the skill
published to Smithery, ClawHub, and skills.sh. `modellix-image-prompt-engineering`
prepares image prompts and is installed from this repository or skills.sh. It
hands generation back to `modellix-design`.

`modellix-ffmpeg`, `modellix-moviepy`, `modellix-social-card`, and `modellix-infographic` are not published as their own Smithery
or ClawHub skills. They ship with the complete plugin and with a checkout of this
repository. A skill-only install of `modellix-design` does not include them. `modellix-social-card` plans prompts for mainstream social cards and hands generation back to `modellix-design`. `modellix-infographic` turns a source into one infographic prompt and hands generation to `modellix-design`.

#### Agent Skills (skills.sh) — any host

Install:

```bash
npx skills add https://github.com/Modellix/modellix-plugin --skill modellix-design
npx skills add https://github.com/Modellix/modellix-plugin --skill modellix-image-prompt-engineering
npx skills add https://github.com/Modellix/modellix-plugin --skill modellix-design --agent cursor   # one agent
```

Update:

```bash
npx skills update
```

#### ClawHub / OpenClaw (skill)

Only `modellix-design` is currently published as a standalone ClawHub skill (skill
registry; separate from the `@modellix/modellix-plugin` package above). Install
the prompt skill from the GitHub repository or as part of the complete plugin.

Install:

```bash
clawhub install modellix-design
# or
openclaw skills install modellix-design
```

Update:

```bash
clawhub update modellix-design
# or
clawhub update --all
```

#### OpenCode

OpenCode’s [plugins](https://opencode.ai/docs/zh-cn/plugins/) are JS/TS event hooks — Modellix does **not** use that path. Use [Agent Skills](https://opencode.ai/docs/skills/) instead. This repo exposes six `.opencode/skills/*` symlinks, one for each skill tree.

Install:

```bash
npx skills add https://github.com/Modellix/modellix-plugin --skill modellix-design
npx skills add https://github.com/Modellix/modellix-plugin --skill modellix-image-prompt-engineering

# Global
mkdir -p ~/.config/opencode/skills
ln -sfn /path/to/modellix-plugin/skills/modellix-design ~/.config/opencode/skills/modellix-design
ln -sfn /path/to/modellix-plugin/skills/modellix-image-prompt-engineering ~/.config/opencode/skills/modellix-image-prompt-engineering
ln -sfn /path/to/modellix-plugin/skills/modellix-ffmpeg ~/.config/opencode/skills/modellix-ffmpeg
ln -sfn /path/to/modellix-plugin/skills/modellix-moviepy ~/.config/opencode/skills/modellix-moviepy
ln -sfn /path/to/modellix-plugin/skills/modellix-social-card ~/.config/opencode/skills/modellix-social-card
ln -sfn /path/to/modellix-plugin/skills/modellix-infographic ~/.config/opencode/skills/modellix-infographic

# Project-local
mkdir -p .opencode/skills
ln -sfn /path/to/modellix-plugin/skills/modellix-design .opencode/skills/modellix-design
ln -sfn /path/to/modellix-plugin/skills/modellix-image-prompt-engineering .opencode/skills/modellix-image-prompt-engineering
ln -sfn /path/to/modellix-plugin/skills/modellix-ffmpeg .opencode/skills/modellix-ffmpeg
ln -sfn /path/to/modellix-plugin/skills/modellix-moviepy .opencode/skills/modellix-moviepy
ln -sfn /path/to/modellix-plugin/skills/modellix-social-card .opencode/skills/modellix-social-card
ln -sfn /path/to/modellix-plugin/skills/modellix-infographic .opencode/skills/modellix-infographic
```

Update:

```bash
npx skills update
# or, for a symlink install:
git -C /path/to/modellix-plugin pull
```

In OpenCode, load a skill by name, for example `skill({ name: "modellix-design" })`.

#### Cursor (skill-only)

When you want the skill without installing the full Cursor plugin:

```bash
npx skills add https://github.com/Modellix/modellix-plugin --skill modellix-design --agent cursor
npx skills add https://github.com/Modellix/modellix-plugin --skill modellix-image-prompt-engineering --agent cursor
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
npx skills add https://github.com/Modellix/modellix-plugin --skill modellix-design
npx skills add https://github.com/Modellix/modellix-plugin --skill modellix-image-prompt-engineering
# Pi also scans ~/.agents/skills/

# or symlink the skill tree
mkdir -p ~/.pi/agent/skills
ln -sfn /path/to/modellix-plugin/skills/modellix-design ~/.pi/agent/skills/modellix-design
ln -sfn /path/to/modellix-plugin/skills/modellix-image-prompt-engineering ~/.pi/agent/skills/modellix-image-prompt-engineering
ln -sfn /path/to/modellix-plugin/skills/modellix-ffmpeg ~/.pi/agent/skills/modellix-ffmpeg
ln -sfn /path/to/modellix-plugin/skills/modellix-moviepy ~/.pi/agent/skills/modellix-moviepy
ln -sfn /path/to/modellix-plugin/skills/modellix-social-card ~/.pi/agent/skills/modellix-social-card
ln -sfn /path/to/modellix-plugin/skills/modellix-infographic ~/.pi/agent/skills/modellix-infographic
```

#### Hermes Agent

[Hermes](https://hermes-agent.nousresearch.com/) consumes the Agent Skill (`SKILL.md`) rather than the full plugin package. Short listing blurb: **Unified API for AI image, video, and audio workflows**.

Install:

```bash
hermes skills install Modellix/modellix-plugin/skills/modellix-design
hermes skills install Modellix/modellix-plugin/skills/modellix-image-prompt-engineering
# or from skills.sh (when listed):
# hermes skills install skills-sh/Modellix/modellix-plugin/modellix-design

# copy / symlink into the Hermes skills tree
mkdir -p ~/.hermes/skills
ln -sfn /path/to/modellix-plugin/skills/modellix-design ~/.hermes/skills/modellix-design
ln -sfn /path/to/modellix-plugin/skills/modellix-image-prompt-engineering ~/.hermes/skills/modellix-image-prompt-engineering
ln -sfn /path/to/modellix-plugin/skills/modellix-ffmpeg ~/.hermes/skills/modellix-ffmpeg
ln -sfn /path/to/modellix-plugin/skills/modellix-moviepy ~/.hermes/skills/modellix-moviepy
ln -sfn /path/to/modellix-plugin/skills/modellix-social-card ~/.hermes/skills/modellix-social-card
ln -sfn /path/to/modellix-plugin/skills/modellix-infographic ~/.hermes/skills/modellix-infographic
```

To reuse a shared Agent Skills directory, add under `skills` in `~/.hermes/config.yaml`:

```yaml
skills:
  external_dirs:
    - ~/.agents/skills
```

Update: re-run `hermes skills install ...`, or `git pull` on a symlink checkout. After install, start a new session and invoke `/modellix` (or load the skill via Hermes skill tools). Set `MODELLIX_API_KEY` in the environment or `~/.hermes/.env`.

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
- Modellix Media Generation needs the host to attach `Authorization: Bearer` to `https://tool.modellix.ai/mcp/media`. The plugin manifests declare the URL only. The Cursor `MODELLIX_API_KEY` variable does not automatically become that header.
- In Cursor, the key can also be set as the `MODELLIX_API_KEY` plugin variable for the CLI and REST paths.
- In Hermes, prefer `~/.hermes/.env` or a session environment variable.
- Prefer session-only keys; persist only when you explicitly ask for it.
- Never commit API keys or print them in logs.

Key resolution order in the CLI: `--api-key` → `MODELLIX_API_KEY` → selected saved profile.

## Image prompt workflow

For a vague image request, first use
`skills/modellix-image-prompt-engineering/`. It turns the idea into a T2I or I2I
brief with a final prompt, on-image text language, aspect/size, and reference-image
roles. It does not recommend a model, authenticate, or submit work.

If the user asked only for a prompt, stop there. If they asked for a generated or
edited image, pass the brief to `skills/modellix-design/`, which owns model schema
checks, credentials, paid-submit safety, waiting, and download. A complete prompt
that the user explicitly marked final can go directly to `modellix-design`.

## Social card workflow

For a cover, thumbnail, or carousel on a named network, use
`skills/modellix-social-card/`. It covers mainstream placements such as
Xiaohongshu, WeChat Official Account, Instagram, X, LinkedIn, YouTube, and
TikTok. The brief has one prompt per card, with the aspect ratio and the exact
on-image text. It does not recommend a model, authenticate, or submit work.

If the user asked only for prompts, stop there. If they asked for the images,
pass each prompt to `skills/modellix-design/`. A poster with no platform stays
on `skills/modellix-image-prompt-engineering/`. A structured infographic belongs
to `skills/modellix-infographic/`.

## Infographic workflow

For a visual summary or information diagram, use `skills/modellix-infographic/`.
It turns a source into one infographic prompt, quotes the facts, and confirms
the structure before the prompt is ready. It does not recommend a model,
authenticate, or submit work. Generation goes to `skills/modellix-design/`.

If the user asked only for a prompt, stop there. If they asked for the image,
pass that prompt to `skills/modellix-design/`.

## Local video and audio edits

`skills/modellix-ffmpeg/` concatenates, trims, reframes, and transcodes files that are already on disk, including downloads from `modellix-design`. It does not generate media or read `MODELLIX_API_KEY`.

Before any `ffmpeg` command, run:

```bash
python3 skills/modellix-ffmpeg/scripts/check_ffmpeg.py --json
```

When `ok` is false, show `install_command` and wait for confirmation. The script does not install FFmpeg, download a binary, or pipe a script into a shell.

## Local composites

`skills/modellix-moviepy/` places titles, lower thirds, and a timed stack of clips and voiceover on files that are already on disk, including downloads from `modellix-design`. Concatenation, trimming, scaling, compression, and subtitle-file burns stay in `skills/modellix-ffmpeg/`. It does not generate media.

Before importing moviepy, run:

```bash
python3 skills/modellix-moviepy/scripts/check_moviepy.py --json
```

When `ok` is false, show `install_command` and wait for confirmation. The script does not install moviepy or Pillow.

## Quick start (CLI)

```bash
modellix-cli doctor --json

modellix-cli model run \
  --model-slug <provider/model> \
  --body '{"prompt":"A cinematic sunset over a futuristic city skyline"}' \
  --wait --timeout 5m --json

modellix-cli task download <task_id> --output-dir ./outputs --json
```

If `task download` fails with a private/reserved network error (common behind local proxies that map CDN hosts into `198.18.0.0/15`), retry with `--allow-private-network` for trusted Modellix CDN hosts, or download the resource URL with `curl`.

`model invoke` remains a compatibility alias of `model run`. Prefer `model run` in new scripts.

## Model selection

The user names the `provider/model` slug. This plugin does not substitute one when they leave it out. Ask, and use `model list` / `modellix_list_models` only when they want to see options.

```bash
modellix-cli model list --type text-to-image --output slugs
modellix-cli model describe <provider/model> --json
modellix-cli model get-schema <provider/model>
```

Request-body schemas come from `modellix-cli model get-schema <slug>` (JSON default; public, no API key). If CLI is unavailable, prefer the plugin Docs MCP when connected; otherwise `docs_url` from `model describe`, or links in [llms.txt](https://docs.modellix.ai/llms.txt).

## Execution guidance

1. When Modellix Media Generation tools are available and the input is not a local file, follow `skills/modellix-design/SKILL.md` and submit once with `modellix_submit_task`. Otherwise run `skills/modellix-design/scripts/preflight.py --json` before the first CLI command; it refreshes to a newer npm `latest` release before any paid submit. Prefer the resolved CLI, otherwise use REST ([API guide](https://docs.modellix.ai/ways-to-use/api.md)).
2. Do not hand-roll `task get` polling loops when `modellix_wait_task`, `model run --wait`, or `task wait` is available.
3. Do not blindly retry a paid submit after an unknown outcome, and do not start a second path for the same request. Check `modellix_get_task` or `modellix-cli task history` first.
4. `preflight.py` owns the automatic update check; `invoke_and_poll.py` pins the resolved executable for the complete submit/wait/download workflow. Update failure retains an existing CLI and never triggers a paid retry.
5. CLI behavior source of truth: [npm modellix-cli](https://www.npmjs.com/package/modellix-cli) and `modellix-cli --help` (not the website CLI guide page, which may lag).

## Security and data handling

Prompts and public media inputs are sent to `https://api.modellix.ai` when a documented CLI or REST generation task is invoked, and to `https://tool.modellix.ai/mcp/media` when Modellix Media Generation is invoked. The host attaches the API key to Media Generation; the plugin manifests do not. Modellix Docs Search is read-only, connects only to `https://docs.modellix.ai/mcp`, and does not receive the API key or submit tasks. Spend-safety hook state contains hashes, model slugs, task ids, and timestamps, never prompts, request bodies, complete commands, or keys. See [SECURITY.md](SECURITY.md) and the [Modellix Privacy Policy](https://www.modellix.ai/privacy).

## Hooks (spend and result safety)

Hosts that support the packaged hook adapters load lightweight guards. Hooks are outside the Agent Plugins 1.0.0 core. Shell guards react only to `modellix-cli` commands. Cursor also asks before a repeated `modellix_submit_task`. Hooks never submit, poll, or download on their own:

| Hook | Trigger | Behavior |
| --- | --- | --- |
| Run guard | Before a `model run` / `model invoke` / `model batch` shell command | Asks for confirmation when the same paid submit repeats in a session, when the same slug was already submitted through Media Generation, or when `model batch` has no `--max-tasks`; suggests `doctor` when no credential is discoverable |
| Media guard | Before and after Cursor `modellix_submit_task` | Asks when that model slug was already submitted in the session via MCP or the CLI, then records the slug and task id |
| Task watch | After a `modellix-cli` command | Records task ids from the output and clears them once `task download` succeeds |
| Stop reminder | When the agent tries to finish | Sends one follow-up if tasks were generated but never downloaded (resource URLs expire in about 7 days) |

Config lives in [`hooks/hooks.json`](hooks/hooks.json) (legacy Open Plugins / Claude Code event names) and [`hooks/cursor-hooks.json`](hooks/cursor-hooks.json) (Cursor event names); each host manifest points at exactly one of them, so a host never runs both. Hook logic is Python 3 stdlib only, while `scripts/run_python_hook.mjs` selects the available Python 3 command across platforms. Per-session state stores command fingerprints, model slugs, and task ids—never prompts or keys—and every hook fails open. Hosts without hook support (Pi, Hermes, OpenCode, Codex) ignore this directory.

Plugin-level `scripts/` holds these hook scripts; the CLI/REST helpers used by the skill live in `skills/modellix-design/scripts/`.

## Slash commands

Hosts that support the packaged command adapters expose eight shortcuts. Commands are outside the Agent Plugins 1.0.0 core; each routes to one of the packaged skills and adds no separate runtime:

| Command | Use it for |
| --- | --- |
| `/modellix:prompt [image idea or existing prompt]` | Prepare an image prompt and brief without submitting |
| `/modellix:image [prompt] [image url]` | Text-to-image, or image editing when input images are given |
| `/modellix:video [prompt] [image or video url]` | Text-to-video, image-to-video, or video-to-video |
| `/modellix:audio [tts\|stt\|sts] [text or audio url]` | Text-to-speech, speech-to-text, or speech-to-speech |
| `/modellix:doctor [profile]` | CLI install, credential resolution, connectivity, balance |
| `/modellix:models [term or slug]` | Find a model and its request-body schema |
| `/modellix:tasks [task id]` | Task status, plus recovery after a timeout or unknown submission |
| `/modellix:download [task id] [dir]` | Fetch results into `./outputs` before the ~7-day expiry |

The three paid commands (`image`, `video`, `audio`) and the user-facing prompt
command set `disable-model-invocation: true`. Hosts without command support (Pi,
Hermes, OpenCode, the ClawHub skill bundle) ignore [`commands/`](commands/) and
keep using the skills.

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
├── package.json                    # npm + ClawHub OpenClaw + Pi package (@modellix/modellix-plugin)
├── openclaw.plugin.json            # OpenClaw package manifest (skills bundle)
├── plugin.json                     # Agent Plugins 1.0.0 portable manifest
├── mcp.json                        # Agent Plugins 1.0.0 MCP servers (streamable-http)
├── .mcp.json                       # Cursor/legacy host MCP adapter (`type: http`)
├── commands/                       # Slash commands (:prompt, :social-card, :infographic, :image, :video, :audio, :doctor, :models, :tasks, :download)
├── rules/                          # Host-extension always-on guardrails (.mdc)
├── hooks/                          # Host adapters: hooks.json (legacy/Claude), cursor-hooks.json (Cursor)
├── scripts/                        # Hook logic (Python stdlib) + cross-platform Node launcher
├── .opencode/skills/modellix-design       # Symlink → skills/modellix-design (OpenCode skill discovery)
├── .opencode/skills/modellix-image-prompt-engineering # Symlink → matching skill tree
├── .opencode/skills/modellix-ffmpeg                       # Symlink → skills/modellix-ffmpeg
├── .opencode/skills/modellix-moviepy                      # Symlink → skills/modellix-moviepy
├── .opencode/skills/modellix-social-card                  # Symlink → skills/modellix-social-card
├── .opencode/skills/modellix-infographic                  # Symlink → skills/modellix-infographic
├── .pi/skills/modellix-design             # Symlink → skills/modellix-design (Pi local skill discovery)
├── .pi/skills/modellix-image-prompt-engineering       # Symlink → matching skill tree
├── .pi/skills/modellix-ffmpeg                         # Symlink → skills/modellix-ffmpeg
├── .pi/skills/modellix-moviepy                        # Symlink → skills/modellix-moviepy
├── .pi/skills/modellix-social-card                    # Symlink → skills/modellix-social-card
├── .pi/skills/modellix-infographic                    # Symlink → skills/modellix-infographic
├── .plugin/plugin.json             # Legacy Open Plugins host adapter
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
│   ├── modellix-design/            # Execution skill (CLI/REST, scripts, references, evals)
│   ├── modellix-image-prompt-engineering/ # Prompt-only image planning skill
│   ├── modellix-ffmpeg/            # Local concat, trim, reframe, and transcode
│   ├── modellix-moviepy/           # Local titles, lower thirds, and timelines
│   ├── modellix-social-card/       # Prompt-only social card planning
│   └── modellix-infographic/       # Prompt-only infographic planning
└── .github/workflows/              # Publish sync (Smithery / skills add / ClawHub)
```

The six immediate skill directories are discovered from the fixed Agent Plugins
`skills/` location without manifest path fields. Pi uses
`package.json#pi.skills`; Hermes installs skill trees directly (no
Hermes-specific plugin manifest). A skill-only install of `modellix-design`
does not include `modellix-ffmpeg`, `modellix-moviepy`, `modellix-social-card`, or `modellix-infographic`. Those skills ship with the plugin package
and are not published as their own Smithery or ClawHub skills.

## Maintaining this plugin

See [AGENTS.md](AGENTS.md) for sources of truth, update checklists, smoke tests, versioning, and PR conventions.

Current plugin version: see [`plugin.json`](plugin.json) (kept in sync with host
manifests and [`skills/modellix-design/skill.json`](skills/modellix-design/skill.json)).
The prompt-only skill, the social-card skill, the infographic skill, the FFmpeg skill, and the moviepy skill have their own versions in
[`skills/modellix-image-prompt-engineering/skill.json`](skills/modellix-image-prompt-engineering/skill.json),
[`skills/modellix-social-card/skill.json`](skills/modellix-social-card/skill.json),
[`skills/modellix-infographic/skill.json`](skills/modellix-infographic/skill.json),
[`skills/modellix-ffmpeg/skill.json`](skills/modellix-ffmpeg/skill.json), and
[`skills/modellix-moviepy/skill.json`](skills/modellix-moviepy/skill.json).

## Links

- Product: [modellix.ai](https://modellix.ai)
- Docs: [docs.modellix.ai](https://docs.modellix.ai)
- Models index: [llms.txt](https://docs.modellix.ai/llms.txt)
- Plugin guide: [ways-to-use/plugin](https://docs.modellix.ai/ways-to-use/plugin)
- Agent skill guide: [ways-to-use/skill](https://docs.modellix.ai/ways-to-use/skill.md)
- Docs Search: [ways-to-use/mcp](https://docs.modellix.ai/ways-to-use/mcp) ([endpoint](https://docs.modellix.ai/mcp))
- Media Generation: [ways-to-use/media-generation-mcp](https://docs.modellix.ai/ways-to-use/media-generation-mcp) ([endpoint](https://tool.modellix.ai/mcp/media))
- REST API: [ways-to-use/api](https://docs.modellix.ai/ways-to-use/api.md)
- CLI package: [npmjs.com/package/modellix-cli](https://www.npmjs.com/package/modellix-cli)
- Plugin package: [npmjs.com/package/@modellix/modellix-plugin](https://www.npmjs.com/package/@modellix/modellix-plugin)
- Pricing: [get-started/pricing](https://docs.modellix.ai/get-started/pricing)
- Support: [support@modellix.ai](mailto:support@modellix.ai)
- Community: [Discord](https://discord.gg/N2FbcB2cZT)
