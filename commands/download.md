---
description: Download Modellix task results to a local directory before the resource URLs expire.
argument-hint: [optional task id] [optional output directory]
---

Download Modellix results. Target: $ARGUMENTS

Read-only against the API: downloading costs nothing and never resubmits a task.

1. Resolve the task id: use the one in `$ARGUMENTS`, otherwise take the most recent successful entry from `modellix-cli task history --limit 20 --json` and say which one you picked.
2. Download to `./outputs` unless `$ARGUMENTS` names a directory:

```bash
modellix-cli task download <task_id> --output-dir ./outputs --json
```

Existing files are preserved by default; pass `--overwrite` only when the user asks for it.

3. If the task is not in a successful terminal state yet, stop and use `/modellix:tasks` to wait — do not submit a new task.
4. If the download fails with a private or reserved network error (common when a local proxy maps `file.modellix.ai` into `198.18.0.0/15`), retry with `--allow-private-network` for trusted Modellix CDN hosts, or fetch `result.resources[].url` with curl and name files `modellix-{model_slug}-{timestamp}.{ext}` (slashes in the slug become hyphens).
5. Resource URLs expire in about 7 days. If they are already gone, say so plainly instead of silently regenerating.
6. Report the local file paths and byte counts.
