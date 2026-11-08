---
description: Plan a product TVC shot list without generating video.
argument-hint: [product, structure, length, or aspect]
disable-model-invocation: true
---

Plan a product commercial for Modellix. Request: $ARGUMENTS

Follow `skills/modellix-tvc/SKILL.md`.

1. If `$ARGUMENTS` is empty, ask which product the film is for. Do not invent a
   product or a claim.
2. Return the skill's complete TVC brief, including one prompt per shot.
3. Stop after prompt preparation. Do not submit a generation task.
4. If the user later asks to generate the film, pass the shot prompts to
   `skills/modellix-design/SKILL.md` in the brief's order.
