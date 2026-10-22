---
description: Plan a knowledge-comic storyboard and page prompts without generating images.
argument-hint: [source, preset, page count, or text level]
disable-model-invocation: true
---

Plan a knowledge comic for Modellix. Request: $ARGUMENTS

Follow `skills/modellix-comic/SKILL.md`.

1. If `$ARGUMENTS` is empty, ask what the comic should explain. Do not invent a
   subject.
2. Return the skill's complete comic brief, including one prompt per page.
3. Stop after prompt preparation. Do not submit a generation task.
4. If the user later asks to generate the pages, pass the prompts to
   `skills/modellix-design/SKILL.md` in the brief's order.
