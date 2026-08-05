---
description: Synthesize, transcribe, or transform speech and audio with Modellix.
argument-hint: [tts|stt|sts] [text or public audio URL]
disable-model-invocation: true
---

Run an audio workflow with Modellix. Request: $ARGUMENTS

Follow the Modellix skill (`skills/modellix/SKILL.md`) for execution policy, credentials, schema lookup, and error handling. This command only fixes the routing.

1. If `$ARGUMENTS` is empty or the intended audio workflow is ambiguous, ask whether the user wants text-to-speech, speech-to-text, or speech-to-speech. Never invent text, a voice, or an input URL.
2. Pick the model:
   - A slug named by the user wins; confirm its schema with `modellix-cli model describe <slug> --json`.
   - Text-to-speech → `alibaba/qwen-audio-3.0-tts-flash`; requires `text` and a Flash-compatible `voice` verified against the live model doc.
   - Speech-to-text → `openai/whisper-1`; requires one public audio `url`.
   - Speech-to-speech / voice clone → `alibaba/cosyvoice-clone`; requires the target CosyVoice `model`, reference audio `url`, and synthesis `text`.
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
