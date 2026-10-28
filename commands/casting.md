---
description: Plan a casting-board prompt without generating an image.
argument-hint: [character, rendering, or aspect]
disable-model-invocation: true
---

Plan a casting board for Modellix. Request: $ARGUMENTS

Follow `skills/modellix-casting/SKILL.md`.

1. If `$ARGUMENTS` is empty, ask who the character is. Do not invent a name or
   a costume.
2. Return the skill's complete casting brief, including the board prompt.
3. Stop after prompt preparation. Do not submit a generation task.
4. If the user later asks to generate the board, pass the prompt to
   `skills/modellix-design/SKILL.md`.
