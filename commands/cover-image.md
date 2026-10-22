---
description: Plan one article-cover prompt without generating the image.
argument-hint: [article title, type, palette, or aspect]
disable-model-invocation: true
---

Plan an article cover prompt for Modellix. Request: $ARGUMENTS

Follow `skills/modellix-cover-image/SKILL.md`.

1. If `$ARGUMENTS` is empty, ask which article the cover is for. Do not invent a
   title.
2. Return the skill's complete cover brief, including one prompt.
3. Stop after prompt preparation. Do not submit a generation task.
4. If the user later asks to generate the image, pass the prompt to
   `skills/modellix-design/SKILL.md`.
