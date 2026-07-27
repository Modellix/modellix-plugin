---
description: Generate a video with Modellix from a prompt, an image, or a source video.
argument-hint: [prompt] [optional image or video URL]
disable-model-invocation: true
---

Generate a video with Modellix. Request: $ARGUMENTS

Follow the Modellix skill (`skills/modellix/SKILL.md`) for execution policy, credentials, and error handling. This command only fixes the routing.

1. If `$ARGUMENTS` is empty, ask for a prompt instead of inventing one.
2. Pick the model:
   - A slug named by the user wins; confirm it with `modellix-cli model describe <slug> --json` if unsure.
   - Text only → `bytedance/seedance-2.0-mini-t2v` (`{"prompt": "..."}`).
   - With an input image → `bytedance/seedance-2.0-fast-i2v` (needs one of `first_frame_image`, `last_frame_image`, `reference_images`).
   - With a source video → `bytedance/seedance-2.0-fast-v2v` (`{"video_urls": ["<url>"]}`).
3. Submit, wait, and persist:

```bash
modellix-cli model run \
  --model-slug <slug> \
  --body '<json>' \
  --wait --timeout 10m --json

modellix-cli task download <task_id> --output-dir ./outputs --json
```

4. One paid submit per invocation. If the outcome is unknown or ambiguous, run `modellix-cli task history` and recover the existing task — never re-run the same submission blindly.
5. Video jobs often outlast the wait window. On exit code 124 the task is still running remotely: recover with `modellix-cli task wait <task_id> --timeout 20m --json`, then download. Do not submit again.
6. Report the model slug, task id, and the local file paths.
