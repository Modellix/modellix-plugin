---
description: Plan social-card prompts for a mainstream network without generating the images.
argument-hint: [platform, source note, or announcement]
disable-model-invocation: true
---

Plan social card prompts for Modellix. Request: $ARGUMENTS

Follow `skills/modellix-social-card/SKILL.md`.

1. If `$ARGUMENTS` is empty, ask which network and what the card should say.
   Do not invent a platform or a claim.
2. Return the skill's complete social card brief, including one prompt per card.
3. Stop after prompt preparation. Do not submit a generation task.
4. If the user later asks to generate the images, pass each prompt to
   `skills/modellix-design/SKILL.md`.
