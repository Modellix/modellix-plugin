#!/usr/bin/env python3
"""stop hook: after a main-branch push, follow up so the agent refreshes community listings."""

from __future__ import annotations

import json
import sys
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parent
STATE_DIR = HOOKS_DIR / "state"
PENDING_PATH = STATE_DIR / "listings-pending.json"
REPORT_PATH = STATE_DIR / "listings-last-report.json"


def emit(obj: dict) -> None:
    sys.stdout.write(json.dumps(obj) + "\n")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:  # noqa: BLE001
        emit({})
        return 0

    if payload.get("status") != "completed":
        emit({})
        return 0
    if int(payload.get("loop_count") or 0) > 0:
        emit({})
        return 0
    if not PENDING_PATH.is_file():
        emit({})
        return 0

    try:
        pending = json.loads(PENDING_PATH.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        PENDING_PATH.unlink(missing_ok=True)
        emit({})
        return 0

    # Consume the pending flag so we only follow up once per push.
    PENDING_PATH.unlink(missing_ok=True)

    needs = pending.get("needs_action") or pending.get("summary", {}).get("needs_action_ids")
    tip = pending.get("tip_sha") or "HEAD"
    ids = pending.get("summary", {}).get("needs_action_ids") or []

    if not needs and not pending.get("errors"):
        followup = (
            "A successful `git push` to main just finished "
            f"(tip `{tip}`). Community listing check reports all tracked awesome-list "
            "skill/plugin entries are already on the current Modellix URLs. Briefly confirm that to the "
            "user in Chinese. Do not open unnecessary PRs."
        )
        emit({"followup_message": followup})
        return 0

    report_hint = ""
    if REPORT_PATH.is_file():
        report_hint = (
            f"Read the JSON report at `{REPORT_PATH.relative_to(HOOKS_DIR.parents[1])}` "
            "for per-target detail. "
        )

    followup = (
        "A successful `git push` to main just finished "
        f"(tip `{tip}`). External skill/plugin-directory listings need attention "
        f"({', '.join(ids) if ids else 'see report'}). "
        f"{report_hint}"
        "Follow the playbook encoded in `.cursor/hooks/community-listings.json` "
        "(not the long section formerly in AGENTS.md):\n"
        "1. Run `python3 .cursor/hooks/sync_community_listings.py --check` and summarize.\n"
        "2. For **stale** `readme_link` targets, run "
        "`python3 .cursor/hooks/sync_community_listings.py --apply` if `gh` is authenticated; "
        "otherwise open update PRs yourself with English titles/bodies, replacing old "
        "`modellix-skill` URLs with the canonical `modellix-plugin` skill/plugin URL.\n"
        "3. For **missing** `readme_link` / `file_entry` / `manual` / `vendored_skill` targets, "
        "open or refresh PRs using each target's `desired_snippet`, `pr_title`, and `notes` "
        "(awesome-opencode: add `data/plugins/modellix.yaml` only; "
        "composio awesome-claude-plugins: README link under Image and Video Generation).\n"
        "4. For **issue_form** targets (awesome-copilot): do **not** PR `plugins/external.json`. "
        "Cut a matching GitHub release tag + full SHA, then open the External plugin issue form "
        "from `issue_url` / notes. Acknowledge paid-API guidance if relevant.\n"
        "5. Reply to the user in Chinese with PR/issue URLs or exact next steps. Do not commit "
        "unrelated files."
    )
    emit({"followup_message": followup})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
