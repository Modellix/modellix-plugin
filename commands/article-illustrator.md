---
description: Plan in-article illustration prompts without generating images.
argument-hint: [article, preset, density, or aspect]
disable-model-invocation: true
---

Plan illustrations for an article on Modellix. Request: $ARGUMENTS

Follow `skills/modellix-article-illustrator/SKILL.md`.

1. If `$ARGUMENTS` is empty, ask which article to illustrate. Do not invent a
   title or a section.
2. Return the skill's complete article illustration brief, including one prompt
   per illustration.
3. Stop after prompt preparation. Do not submit a generation task.
4. If the user later asks to generate the illustrations, pass the prompts to
   `skills/modellix-design/SKILL.md` in the brief's order.
