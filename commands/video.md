---
description: Generate a video with Modellix from a prompt, an image, or a source video.
argument-hint: [prompt] [optional image or video URL]
disable-model-invocation: true
---

Generate a video with Modellix. Request: $ARGUMENTS

Follow the Modellix skill (`skills/modellix-design/SKILL.md`) for execution policy, credentials, and error handling. This command only fixes the routing. Use Media Generation when `modellix_submit_task` is available and the input is not a local file. The CLI steps below apply when the skill selects the CLI path.

1. If `$ARGUMENTS` is empty, ask for a prompt instead of inventing one.
2. Pick the model:
   - Use a slug the user named, and confirm its request contract with `modellix-cli model get-schema <slug>` before building `--body`.
   - If they did not name a slug, ask for one.
   - Text-only bodies need `prompt`. An input image needs one of `first_frame_image`, `last_frame_image`, or `reference_images`. A source video needs `video_urls`.
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
