---
description: Synthesize, transcribe, or transform speech and audio with Modellix.
argument-hint: [tts|stt|sts] [text or public audio URL]
disable-model-invocation: true
---

Run an audio workflow with Modellix. Request: $ARGUMENTS

Follow the Modellix skill (`skills/modellix-design/SKILL.md`) for execution policy, credentials, schema lookup, and error handling. This command only fixes the routing. Use Media Generation when `modellix_submit_task` is available and the input is not a local file. The CLI steps below apply when the skill selects the CLI path.

1. If `$ARGUMENTS` is empty or the intended audio workflow is ambiguous, ask whether the user wants text-to-speech, speech-to-text, or speech-to-speech. Never invent text, a voice, or an input URL.
2. Pick the model:
   - Use a slug the user named, and confirm its request contract with `modellix-cli model get-schema <slug>` before building `--body`.
   - If they did not name a slug, ask for one.
   - Text-to-speech needs `text` and a `voice` from that model's schema.
   - Speech-to-text needs one public audio `url`.
   - Speech-to-speech needs the fields that slug's schema requires, including reference audio and synthesis text when those are required.
3. Submit, wait, and persist:

```bash
modellix-cli model run \
  --model-slug <slug> \
  --body '<json>' \
  --wait --timeout 10m --json

modellix-cli task download <task_id> --output-dir ./outputs --json
```

4. One paid submit per invocation. If the outcome is unknown or ambiguous, run `modellix-cli task history` and recover the existing task—never repeat the same submission blindly.
5. Report the model slug, task id, and either the local audio paths or the returned transcript resource.
