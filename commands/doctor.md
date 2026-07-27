---
description: Check the Modellix CLI install, credential resolution, API connectivity, and balance.
argument-hint: [optional profile name]
---

Diagnose the Modellix setup. Optional profile: $ARGUMENTS

Read-only: never submit a paid task from this command.

1. Check the CLI, and offer `npm i -g modellix-cli@latest` if it is missing:

```bash
modellix-cli --version
modellix-cli doctor --json
```

Add `--profile $ARGUMENTS` when a profile was given.

2. Read the report: Node.js version, key source, API connectivity, key validity, balance. `doctor` never prints the key itself.
3. If no credential resolves, follow the API key lifecycle in `skills/modellix/SKILL.md`: discover the session env `MODELLIX_API_KEY` and saved profiles first, ask the user only when nothing is available, and keep it session-only unless they ask to persist (`modellix-cli auth login`).
4. If the CLI cannot be installed, say so and note that the REST fallback in `skills/modellix/references/rest-playbook.md` needs `MODELLIX_API_KEY`.
5. Summarize what passed, what failed, and the single next action. Never echo the key.
