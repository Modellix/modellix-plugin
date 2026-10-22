---
description: Plan a vertical ecommerce UGC video without generating it.
argument-hint: [product, pattern, language, or length]
disable-model-invocation: true
---

Plan an ecommerce UGC video for Modellix. Request: $ARGUMENTS

Follow `skills/modellix-ecomm-ugc-video/SKILL.md`.

1. If `$ARGUMENTS` is empty, ask which product the video is for. Do not invent a
   product or a claim.
2. Return the skill's complete UGC brief, including one prompt per shot.
3. Stop after prompt preparation. Do not submit a generation task.
4. If the user later asks to generate the video, pass each shot prompt to
   `skills/modellix-design/SKILL.md`.
