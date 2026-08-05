---
description: Find Modellix models and their request-body schema before running a task.
argument-hint: [search term, model type, provider, or full slug]
---

Find a Modellix model. Query: $ARGUMENTS

Read-only: never submit a paid task from this command.

1. If `$ARGUMENTS` looks like a full `provider/model` slug, describe it directly:

```bash
modellix-cli model describe $ARGUMENTS --json
```

2. Otherwise search the catalog, using the filter that matches the query:

```bash
modellix-cli model list --search <term> --limit 20 --json
modellix-cli model list --type text-to-image --output slugs
modellix-cli model list --provider <provider> --limit 20 --json
```

Common types include `text-to-image`, `image-to-image`, `text-to-video`, `image-to-video`, `video-to-video`, `text-to-speech`, `speech-to-text`, and `speech-to-speech`. Treat the live catalog as authoritative.

3. For the request-body schema, read the model docs: prefer the Docs MCP when the host has it connected, otherwise the `docs_url` returned by `model describe`, or the matching entry in https://docs.modellix.ai/llms.txt.
4. Never invent a slug from a documentation filename — decimals matter (`bytedance/seedance-2.0-mini-t2v`, not `seedance-2-0-mini-t2v`).
5. Report the candidate slugs, what each is good for, and the required body fields. Then point at `/modellix:image`, `/modellix:video`, or `/modellix:audio` to run one.
