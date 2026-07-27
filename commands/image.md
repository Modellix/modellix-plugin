---
description: Generate an image with Modellix, or edit one when input images are given.
argument-hint: [prompt] [optional image URL or path]
disable-model-invocation: true
---

Generate an image with Modellix. Request: $ARGUMENTS

Follow the Modellix skill (`skills/modellix/SKILL.md`) for execution policy, credentials, and error handling. This command only fixes the routing.

1. If `$ARGUMENTS` is empty, ask for a prompt instead of inventing one.
2. Pick the model:
   - A slug named by the user wins; confirm it with `modellix-cli model describe <slug> --json` if unsure.
   - Text only → `google/nano-banana-2-lite` (`{"prompt": "..."}`).
   - With input images → `google/nano-banana-2-lite-edit` (`{"prompt": "...", "image": ["<url>"]}`).
3. Submit, wait, and persist:

```bash
modellix-cli model run \
  --model-slug <slug> \
  --body '<json>' \
  --wait --timeout 5m --json

modellix-cli task download <task_id> --output-dir ./outputs --json
```

4. One paid submit per invocation. If the outcome is unknown or ambiguous, run `modellix-cli task history` and recover the existing task — never re-run the same submission blindly.
5. If the download fails with a private or reserved network error, retry with `--allow-private-network` for trusted Modellix CDN hosts, or fetch `result.resources[].url` with curl.
6. Report the model slug, task id, and the local file paths.
