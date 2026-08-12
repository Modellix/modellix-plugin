# Security and Data Handling

## Report a vulnerability

Please report security issues privately to [support@modellix.ai](mailto:support@modellix.ai). Include the affected plugin version, host, operating system, reproduction steps, and impact. Do not include API keys, private prompts, or customer media in the report.

The latest released version receives security fixes. Please update before reporting an issue that may already be resolved.

## Credential handling

- The primary credential is `MODELLIX_API_KEY`. The CLI may alternatively use its saved credential profile.
- The plugin never prints, commits, or writes raw API keys into hook state.
- Session-only environment credentials are the default. Persistent login through `modellix-cli auth login` or `init` requires an explicit user request.
- The optional Python wrapper passes an explicit key to a child CLI process through `MODELLIX_API_KEY`, not a process argument.

## Network and user data

- Before the first CLI use in a workflow, `preflight.py` queries only the public npm registry for `modellix-cli@latest`. If a newer version is available, it globally installs that exact version with lifecycle scripts disabled, then verifies the CLI-reported version before use. Set `MODELLIX_CLI_AUTO_UPDATE=0` to opt out.
- npm registry checks and installs use a clean public-registry configuration that removes npm auth/token/password environment variables and does not read the user's npm config. Update failures retain a working installed CLI; the updater never downgrades and never runs after a paid submit has started.
- Generation, editing, transcription, and speech inputs are sent only when a user or agent invokes the documented Modellix CLI or REST workflow. Prompts and public media URLs are sent to `https://api.modellix.ai`.
- Result downloads may connect to the HTTPS resource hosts returned by the Modellix API, including `file.modellix.ai`. Generated results are retained for about seven days; save required outputs promptly.
- The optional Docs MCP connects only to `https://docs.modellix.ai/mcp` for documentation search and reading. It does not receive the Modellix API key and cannot submit paid tasks.
- This plugin adds no analytics or unrelated network requests. See the [Modellix Privacy Policy](https://www.modellix.ai/privacy) for the service-level policy.

## Local state

Spend-safety hooks keep a small file under the operating-system temporary directory. It contains hashed command fingerprints, model slugs, task ids, timestamps, and reminder flags. It never contains request bodies, prompts, media, API keys, or complete shell commands. State expires after 24 hours, and stale files are removed when hooks next load or save state.

The CLI updater uses a user-local cache/state directory only for npm cache data and a short-lived concurrency lock; it does not store Modellix or npm credentials.

Repository-level maintainer hooks and marketing follow-ups are intentionally excluded from the installable plugin artifact.

## Paid-operation safety

- Paid model submissions are never automatically retried by the bundled wrapper.
- An ambiguous submission must be recovered through task history, the Modellix console, or a known task id before another paid POST.
- Batch commands require an explicit task ceiling or user acknowledgement.
- Hooks fail open on runtime errors; they advise or request confirmation but never run a paid command themselves.
