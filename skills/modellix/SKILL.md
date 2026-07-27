---
name: modellix
description: Integrate Modellix's unified API for AI image and video generation into applications. Use this skill whenever the user wants to generate images from text, create videos from text or images, edit images, do virtual try-on, or call any Modellix model API. Also trigger when the user mentions Modellix, model-as-a-service for media generation, or needs to work with providers like Qwen, Wan, Seedream, Seedance, Kling, Hailuo, or MiniMax through a unified API. Prefer modellix-cli (model run --wait, task download, doctor, model list) over hand-rolled REST polling whenever the CLI is available.
primaryCredential: MODELLIX_API_KEY
primaryEnv: MODELLIX_API_KEY
requiredEnv:
  - MODELLIX_API_KEY
---

# Modellix Skill

Modellix is a Model-as-a-Service (MaaS) platform for async image/video generation. Prefer the official CLI (`modellix-cli`) so submit, wait, and download stay one coherent workflow.

## Official Docs

- AI Onboarding: https://docs.modellix.ai/get-started.md
- REST API: https://docs.modellix.ai/ways-to-use/api.md
- Full Models Index: https://docs.modellix.ai/llms.txt
- CLI package (source of truth for CLI behavior): https://www.npmjs.com/package/modellix-cli

Do not rely on the website CLI guide page for command syntax; use this skill, `references/cli-playbook.md`, npm README, or `modellix-cli --help`.

## Execution Policy (CLI-first)

Choose the path in this order:

1. **CLI** when `modellix-cli` is available (install with `npm i -g modellix-cli@latest` if missing and install is allowed).
2. **REST** only when CLI is not installed, unsuitable, or missing a needed capability.
3. Prefer machine-readable output (`--json` or `--quiet`) for automation.

Canonical single-task flow:

```bash
modellix-cli doctor --json
modellix-cli model run \
  --model-slug <provider/model> \
  --body '<json>' \
  --wait --timeout 5m --json
modellix-cli task download <task_id> --output-dir ./outputs --json
```

`model invoke` is a compatibility alias of `model run`. New commands should use `model run`.

Do not reinvent polling loops when CLI wait is available. Do not invent deprecated flags (for example `--model-type`). Use `--help` only when behavior is unclear.

## Default Models

When the user does **not** name a model, use these defaults immediately (do not scan the catalog first):

| Task Type | Default Model Slug |
|---|---|
| Text-to-image (T2I) | `google/nano-banana-2-lite` |
| Text-to-video (T2V) | `bytedance/seedance-2.0-mini-t2v` |
| Image editing / I2I | `bytedance/seedream-5.0-lite-edit` |
| Image-to-video / I2V | `bytedance/seedance-2.0-fast-i2v` |
| Video-to-video (V2V) | `bytedance/seedance-2.0-v2v` |

## API Key Lifecycle Policy

Handle credentials as: `discover -> request -> use-session -> (optional) persist`.

### 1) Discover existing key first

Before asking the user:

1. Session / process env `MODELLIX_API_KEY`
2. Saved CLI profile (`modellix-cli auth status` / `doctor` — key via `--profile` or `MODELLIX_PROFILE` or `currentProfile`)
3. If still missing, request a key from the user

Never ask again when a usable key is already discoverable. CLI key resolution order is: `--api-key` → `MODELLIX_API_KEY` → selected saved profile.

### 2) Request key only when missing

- Ask for a key from [Modellix Console](https://modellix.ai/console/api-key).
- Do not print or echo key values.
- Prefer session env for the current run.

### 3) Optional persistence

Default: do not persist automatically.

When the user explicitly asks to persist:

1. Preferred: `modellix-cli auth login` or `modellix-cli init` (CLI validates and stores the profile securely).
2. Alternative: user-level `MODELLIX_API_KEY` only if they insist on env persistence.
3. Do not write system-level env or other agents' config files.

### 4) Key rotation

If the user provides a new key: update session first; if they requested persistence, replace via `auth login`/`init` (or user-level env). Re-check with `modellix-cli doctor --json` (or `scripts/preflight.py --json`) before continuing.

## Preflight and Deterministic Execution

Preferred checks:

```bash
modellix-cli doctor --json
```

Bundled helpers (optional):

1. `scripts/preflight.py` — wraps `doctor` when CLI exists; otherwise lightweight env/`which` checks and recommends `cli` or `rest`.
2. `scripts/invoke_and_poll.py` — CLI path uses `model run --wait`; REST path keeps submit+poll fallback.

When preflight/doctor reports missing credentials, apply the lifecycle above.

When CLI is unavailable:

1. Use REST (`references/rest-playbook.md`).
2. After the task, recommend: `npm i -g modellix-cli@latest`.

## Core Workflow

### 1) Ready the environment

- Discover or request API key (lifecycle above).
- Run `modellix-cli doctor --json` when CLI is present.
- Continue only when auth and connectivity look healthy (or REST key is set).

### 2) Select model

1. If the user did not specify a model: use the **Default Models** table (do not scan the catalog first).
2. If they named a model or need discovery: `modellix-cli model list` / `modellix-cli model describe <slug>` (describe returns `docs_url`).
3. If CLI is unavailable: browse https://docs.modellix.ai/llms.txt for links, then fetch the target model `.md`.
4. For request body schema: fetch the model doc (`docs_url` or the matching docs link) and read the OpenAPI path / `model_id`. Do **not** invent slugs from filenames (decimals often matter, e.g. `bytedance/seedance-2.0-mini-t2v`).

### 3) Run and wait

Default (single task):

```bash
modellix-cli model run \
  --model-slug google/nano-banana-2-lite \
  --body '{"prompt":"A cinematic sunset over a futuristic city skyline"}' \
  --wait --timeout 5m --json
```

Split flow when useful (pipelines, concurrency):

```bash
TASK_ID=$(modellix-cli model run --model-slug ... --body '...' --output task-id)
modellix-cli task wait "$TASK_ID" --timeout 10m --json
```

Batch (paid guard required): `modellix-cli model batch tasks.jsonl --max-tasks N [--wait]`.

Manual REST: `references/rest-playbook.md`. Optional helper: `scripts/invoke_and_poll.py`.

### 4) Download results

```bash
modellix-cli task download <task_id> --output-dir ./outputs --json
```

If download fails with `Resource host resolves to a private or reserved network address` (common when a local proxy/VPN maps CDN hosts like `file.modellix.ai` into `198.18.0.0/15`), retry with `--allow-private-network` for trusted Modellix CDN hosts, or fall back to downloading the `result.resources[].url` with `curl`/`wget`.

Resource URLs expire in about 24 hours — persist promptly. If downloading manually (REST path), name files:

```
modellix-{model_slug}-{timestamp}.{ext}
```

(replace `/` in the slug with `-`).

Examples:

- `modellix-google-nano-banana-2-lite-20260430-113000.png`
- `modellix-bytedance-seedance-2.0-mini-t2v-20260430-113500.mp4`

### Quick Examples

**T2I** (default model) — `prompt` required:

```bash
modellix-cli model run \
  --model-slug google/nano-banana-2-lite \
  --body '{"prompt":"A cinematic sunset over a futuristic city skyline"}' \
  --wait --timeout 5m --json
```

**T2V** (default model) — `prompt` required:

```bash
modellix-cli model run \
  --model-slug bytedance/seedance-2.0-mini-t2v \
  --body '{"prompt":"A cat playing in a sunny garden"}' \
  --wait --timeout 10m --json
```

**I2I** — `prompt` + `image` array:

```bash
modellix-cli model run \
  --model-slug bytedance/seedream-5.0-lite-edit \
  --body '{"prompt":"Convert to watercolor style","image":["https://example.com/input.jpg"]}' \
  --wait --timeout 5m --json
```

**I2V** — at least one image param (`first_frame_image`, `last_frame_image`, or `reference_images`):

```bash
modellix-cli model run \
  --model-slug bytedance/seedance-2.0-fast-i2v \
  --body '{"prompt":"A cat playing in the garden","first_frame_image":"https://example.com/frame.jpg"}' \
  --wait --timeout 10m --json
```

**V2V** — `video_urls` array:

```bash
modellix-cli model run \
  --model-slug bytedance/seedance-2.0-v2v \
  --body '{"video_urls":["https://example.com/source.mp4"]}' \
  --wait --timeout 10m --json
```

### 5) Post-task CLI recommendation

If this session used REST because CLI was missing, suggest installing the CLI afterward.

## Progressive Reference Routing

Read only what the task needs:

- `references/cli-playbook.md` — install, auth, run/wait/download, batch, recovery
- `references/rest-playbook.md` — REST submit/poll when CLI is unavailable
- `references/capability-matrix.md` — CLI ↔ REST mapping and fallback rules

## Bundled Assets

- `assets/output/task-result.schema.json`

## Credential and Data Egress

- Primary credential: `MODELLIX_API_KEY` (also via CLI profiles).
- Network egress: `https://api.modellix.ai` (override only with trusted `--base-url` / `MODELLIX_BASE_URL`).
- User prompts and media inputs may be sent to Modellix during invocation.
- Never expose API keys in logs, screenshots, transcripts, or commits.
- Default to session-only credentials; persistent writes need explicit user approval.

## Error / Retry Policy

| Situation | Action |
|------|--------|
| HTTP/API `400` | Do not retry. Fix parameters or body. |
| `401` | Do not retry. Fix key (`doctor`, `auth login`). |
| `402` | Do not retry. Insufficient balance. |
| `404` | Do not retry. Verify `task_id` or model slug. |
| `429` / read-only `5xx` | CLI already retries safe GETs within deadline; do not blindly re-POST paid submits. |
| Paid submit outcome **unknown** | Do **not** immediately re-run the same `model run`. Check `task history`, console activity, and any printed task ID first. |
| Exit `124` | Local wait timeout; remote task may still run — recover with `task wait` / `task get`, then `task download`. |
| Exit `2` | Argument or safety guard (e.g. batch cost limit) — fix flags. |

## Verification Checklist

- [ ] Doctor/preflight passed or REST key ready
- [ ] Model chosen (default table or user/catalog)
- [ ] Body schema checked against model doc when non-trivial
- [ ] Used `model run --wait` (or `task wait`) instead of hand-rolled poll loops
- [ ] Results downloaded (`task download` or manual persist before 24h expiry)
- [ ] No blind retry after unknown paid submission
- [ ] REST used only when CLI path unavailable
