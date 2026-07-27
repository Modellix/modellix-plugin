---
description: Inspect Modellix task status and recover tasks after a timeout or unknown submission.
argument-hint: [optional task id]
---

Inspect Modellix tasks. Target: $ARGUMENTS

Read-only: never submit a new paid task from this command — recovery means finding the task that already exists.

1. Without a task id, list what this machine recorded:

```bash
modellix-cli task history --limit 20 --json
```

History stores task id, profile, API origin, model slug, status, and timestamps — never keys or request bodies.

2. With a task id, read its current state:

```bash
modellix-cli task get $ARGUMENTS --json
```

3. If it is still running, wait instead of resubmitting:

```bash
modellix-cli task wait $ARGUMENTS --interval 5s --timeout 10m --json
```

Exit code 124 means the local wait timed out, not that the task failed; wait again or check back later.

4. After an unknown or ambiguous paid submission, this is the recovery path: match the model slug and timestamp in history, confirm with `task get`, and only submit again once you are sure nothing was accepted.
5. For any task that reached a successful terminal state, hand off to `/modellix:download` — resource URLs expire in about 7 days.
6. Report each task's id, model slug, status, and the next action.
