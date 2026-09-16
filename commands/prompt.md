---
description: Engineer an execution-ready prompt and visual brief for an AI image without generating it.
argument-hint: [image idea, existing prompt, or edit request]
disable-model-invocation: true
---

Prepare an image prompt for Modellix. Request: $ARGUMENTS

Follow `skills/modellix-image-prompt-engineering/SKILL.md`.

1. If `$ARGUMENTS` is empty, ask what image the user wants and where it will be
   used. Do not invent a subject.
2. Return the skill's complete T2I or I2I handoff brief.
3. Stop after prompt preparation. Do not submit a generation task.
4. If the user later asks to generate the image, pass the brief to
   `skills/modellix-design/SKILL.md`.
