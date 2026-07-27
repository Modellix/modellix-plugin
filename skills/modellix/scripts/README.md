# Scripts

These scripts are optional helpers for automation. The default execution path is the CLI:

`modellix-cli model run --wait` → `modellix-cli task download`

## preflight.py

Environment check for CLI-first routing. Prefers `modellix-cli doctor --json` when the CLI is installed.

Usage:

```bash
python scripts/preflight.py
python scripts/preflight.py --json
```

Checks:

- `modellix-cli` availability
- Doctor result (Node, auth source, connectivity, balance) when CLI exists
- `MODELLIX_API_KEY` / discoverable profile auth
- Recommended mode (`cli` or `rest`)

Credential handling policy:

- Default to session-only `MODELLIX_API_KEY` usage.
- Persist with explicit user approval via `modellix-cli auth login` / `init` (preferred) or user-level env.
- Do not write system-level env vars or other agent config files.

## invoke_and_poll.py

Optional wrapper: CLI uses `model run --wait`; REST keeps submit + poll fallback.
If this script fails, switch to the direct CLI commands and continue.

Usage:

```bash
python scripts/invoke_and_poll.py \
  --model-slug google/nano-banana-2-lite \
  --body '{"prompt":"A cinematic portrait of a fox in a misty forest at sunrise"}'

python scripts/invoke_and_poll.py \
  --model-slug bytedance/seedance-2.0-mini-t2v \
  --body '{"prompt":"A cat in a garden"}' \
  --timeout 10m \
  --output-dir ./outputs
```

Key behavior:

- Mode `auto` (default): use CLI when installed, otherwise REST
- CLI path: single `modellix-cli model run --wait --json` (no hand-rolled poll loop; no paid-submit auto-retry)
- Optional `--output-dir` triggers `task download` after a successful CLI wait
- REST path: submit with limited retries on `429/500/503`, then poll until terminal
- `--model-slug` is required in `provider/model` format
- Skill defaults when user omits a model: T2I=`google/nano-banana-2-lite`, T2V=`bytedance/seedance-2.0-mini-t2v`
