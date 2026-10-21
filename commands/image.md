---
description: Generate an image with Modellix, or edit one when input images are given.
argument-hint: [prompt] [optional image URL or path]
disable-model-invocation: true
---

Generate an image with Modellix. Request: $ARGUMENTS

Follow the Modellix skill (`skills/modellix-design/SKILL.md`) for execution policy, credentials, and error handling. This command only fixes the routing. Use Media Generation when `modellix_submit_task` is available and the input is not a local file. The CLI steps below apply when the skill selects the CLI path.

1. If `$ARGUMENTS` is empty, ask for a prompt instead of inventing one.
2. Pick the model:
   - Use a slug the user named, and confirm its request contract with `modellix-cli model get-schema <slug>` before building `--body`.
   - If they did not name a slug, ask for one. Text-only bodies need `prompt`. Image edits need `prompt` and `image`.
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
