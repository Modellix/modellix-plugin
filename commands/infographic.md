---
description: Plan one infographic prompt from a source without generating the image.
argument-hint: [source text, comparison, sequence, or funnel]
disable-model-invocation: true
---

Plan an infographic prompt for Modellix. Request: $ARGUMENTS

Follow `skills/modellix-infographic/SKILL.md`.

1. If `$ARGUMENTS` is empty, ask what the infographic should explain. Do not
   invent facts.
2. Return the skill's complete infographic brief, including one prompt.
3. Stop after prompt preparation. Do not submit a generation task.
4. If the user later asks to generate the image, pass the prompt to
   `skills/modellix-design/SKILL.md`.
