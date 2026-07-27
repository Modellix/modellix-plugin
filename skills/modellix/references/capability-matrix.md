# Capability Matrix

Use this matrix to switch between CLI and REST without changing task semantics.

| Capability | CLI | REST | Notes |
| --- | --- | --- | --- |
| Diagnose env / auth | `modellix-cli doctor --json` | N/A (manual key + probe) | Prefer CLI doctor when installed |
| List / describe models | `model list`, `model describe <slug>` | Browse `llms.txt`, then fetch model `.md` | Prefer CLI when installed; `describe` includes `docs_url` for schema fetch |
| Submit async task | `modellix-cli model run --model-slug <provider/model> --body/--body-file ...` | `POST /api/v1/{provider}/{model_id}/async` | `model invoke` is an alias of `model run` |
| Wait for terminal status | `model run --wait` or `task wait <task_id>` | Poll `GET /api/v1/tasks/{task_id}` | Prefer CLI wait; do not hand-roll poll loops when CLI exists |
| Read task once | `task get <task_id>` | `GET /api/v1/tasks/{task_id}` | Same status lifecycle: `pending` / `processing` / `success` / `failed` |
| Download resources | `task download <task_id> --output-dir ...` | Download URLs from `result.resources` | CLI path preferred (safe filenames, limits) |
| Batch submit | `model batch <file.jsonl> --max-tasks N` | Multiple REST POSTs | CLI validates all lines before first paid POST |
| Local task recovery | `task history` | N/A | Never stores API keys or bodies |

CLI command policy:

- Canonical single-task flow: `model run --wait` → `task download`.
- Split flow when needed: `model run --output task-id` → `task wait` → `task download`.
- Do not use deprecated guessed flags (for example `--model-type`).
- Use `--help` only when behavior is unclear.
- Python wrappers are optional helpers and must not block CLI execution.
- Paid POST submissions must not be blindly retried on unknown outcomes.

## Slug Mapping

- `model-slug` uses `provider/model` format for both CLI and REST.
- REST path transformation:
  - Input: `google/nano-banana-2-lite`
  - Derived path parts: `provider=google`, `model_id=nano-banana-2-lite`

## Default Models (when user omits model)

| Task Type | Default slug |
| --- | --- |
| T2I | `google/nano-banana-2-lite` |
| T2V | `bytedance/seedance-2.0-mini-t2v` |
| I2I | `bytedance/seedream-5.0-lite-edit` |
| I2V | `bytedance/seedance-2.0-fast-i2v` |
| V2V | `bytedance/seedance-2.0-v2v` |

## Fallback Rules

Use REST when any condition is true:

- `modellix-cli` not installed (and cannot be installed)
- CLI auth unavailable
- CLI command surface does not expose required behavior

If CLI is not installed, use REST directly. After the task completes, recommend CLI installation: `npm i -g modellix-cli@latest`.

Otherwise use CLI-first.
