#!/usr/bin/env python3
"""Check / refresh Modellix listings in external skill and plugin directories.

Usage:
  python3 .cursor/hooks/sync_community_listings.py --check
  python3 .cursor/hooks/sync_community_listings.py --apply
  python3 .cursor/hooks/sync_community_listings.py --check --json

--check (default): read-only status against public GitHub contents.
--apply: for targets with stale URLs, open update PRs via `gh` when available.
         Missing first-time listings (and issue_form targets) are reported for the
         agent to create (not auto-appended / not auto-issued).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

HOOKS_DIR = Path(__file__).resolve().parent
REPO_ROOT = HOOKS_DIR.parents[1]
CONFIG_PATH = HOOKS_DIR / "community-listings.json"
STATE_DIR = HOOKS_DIR / "state"
DEFAULT_BRANCH_CACHE: dict[str, str] = {}


def load_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def github_raw(repo: str, path: str, ref: str = "HEAD") -> tuple[str | None, str | None]:
    """Return (text, error). Uses Contents API when GITHUB_TOKEN/GH_TOKEN set, else raw.githubusercontent."""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    headers = {"User-Agent": "modellix-plugin-listings-sync", "Accept": "application/vnd.github.raw+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        url = f"https://api.github.com/repos/{repo}/contents/{path}?ref={ref}"
    else:
        url = f"https://raw.githubusercontent.com/{repo}/{ref}/{path}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="replace"), None
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None, "missing"
        return None, f"HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


def default_branch(repo: str) -> str:
    if repo in DEFAULT_BRANCH_CACHE:
        return DEFAULT_BRANCH_CACHE[repo]
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    headers = {"User-Agent": "modellix-plugin-listings-sync", "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            branch = data.get("default_branch") or "main"
    except Exception:  # noqa: BLE001
        branch = "main"
    DEFAULT_BRANCH_CACHE[repo] = branch
    return branch


def has_stale(text: str, stale_substrings: list[str]) -> bool:
    return any(s in text for s in stale_substrings)


def classify_target(target: dict[str, Any], canonical: dict[str, Any]) -> dict[str, Any]:
    repo = target["repo"]
    path = target["path"]
    branch = default_branch(repo)
    text, err = github_raw(repo, path, branch)
    result: dict[str, Any] = {
        "id": target["id"],
        "repo": repo,
        "path": path,
        "kind": target["kind"],
        "pr_title": target.get("pr_title"),
        "example_pr": target.get("example_pr"),
        "notes": target.get("notes"),
        "status": "unknown",
        "action": None,
        "detail": None,
    }

    if err == "missing" or text is None and err == "missing":
        result["status"] = "missing"
        if target["kind"] == "issue_form":
            result["action"] = "create_issue"
            result["detail"] = (
                f"{path} has no Modellix entry on {repo}@{branch}; open the External plugin "
                f"issue form: {target.get('issue_url') or 'see notes'}"
            )
            result["issue_url"] = target.get("issue_url")
        else:
            result["action"] = "create_pr"
            result["detail"] = f"{path} not found on {repo}@{branch}; needs first-time listing PR"
        if target.get("desired_snippet"):
            result["desired_snippet"] = target["desired_snippet"]
        return result
    if text is None:
        result["status"] = "error"
        result["detail"] = err
        return result

    match_re = re.compile(target.get("match_regex") or "(?i)modellix")
    matched_lines = [ln for ln in text.splitlines() if match_re.search(ln)]
    stale = has_stale(text, canonical.get("stale_url_substrings") or [])

    if target["kind"] == "vendored_skill":
        desired_source = target.get("desired_source_repo", "Modellix/modellix-plugin")
        if not matched_lines and "name: modellix" not in text.lower():
            result["status"] = "missing"
            result["action"] = "create_pr"
            result["detail"] = "Vendored skills/modellix/SKILL.md missing"
            return result
        if desired_source not in text or stale:
            result["status"] = "stale"
            result["action"] = "update_pr"
            result["detail"] = f"Update source_repo / URLs to {desired_source}"
            return result
        result["status"] = "ok"
        result["detail"] = "Vendored skill present with current source_repo"
        return result

    if target["kind"] == "file_entry":
        desired = target.get("desired_snippet") or ""
        if not matched_lines:
            result["status"] = "missing"
            result["action"] = "create_pr"
            result["detail"] = f"{path} exists but has no Modellix match"
            result["desired_snippet"] = desired
            return result
        desired_ok = (not desired) or (
            desired in text
            or desired.rstrip("\n") in text
            or (desired.rstrip("\n") + "\n") in text
        )
        if stale or not desired_ok:
            result["status"] = "stale"
            result["action"] = "update_pr"
            result["detail"] = "File present but content/URLs are outdated"
            result["desired_snippet"] = desired
            return result
        result["status"] = "ok"
        result["detail"] = f"{path} present with current content"
        return result

    if target["kind"] == "issue_form":
        if not matched_lines:
            result["status"] = "missing"
            result["action"] = "create_issue"
            result["detail"] = (
                "Not listed in plugins/external.json yet; submit via External plugin issue form "
                f"({target.get('issue_url') or 'see notes'}). Do not PR external.json."
            )
            result["issue_url"] = target.get("issue_url")
            return result
        if stale:
            result["status"] = "stale"
            result["action"] = "create_issue"
            result["detail"] = (
                "Listed but URLs look stale; open a follow-up issue or maintainer-approved "
                "external.json update PR after cutting a new release tag."
            )
            result["issue_url"] = target.get("issue_url")
            return result
        result["status"] = "ok"
        result["detail"] = "Listed in plugins/external.json"
        return result

    if not matched_lines:
        result["status"] = "missing"
        result["action"] = "create_pr"
        result["detail"] = "No Modellix entry found"
        return result

    desired = target.get("desired_snippet") or ""
    if desired and desired in text and not stale:
        result["status"] = "ok"
        result["detail"] = "Entry present with current URL"
        return result

    if stale or (desired and desired not in text):
        result["status"] = "stale"
        result["action"] = "update_pr"
        result["detail"] = "Entry present but URL/text is outdated"
        result["matched_lines"] = matched_lines[:5]
        result["desired_snippet"] = desired
        return result

    result["status"] = "ok"
    result["detail"] = "Entry present"
    return result


def check_all(config: dict[str, Any]) -> dict[str, Any]:
    canonical = config["canonical"]
    targets = [classify_target(t, canonical) for t in config["targets"]]
    needs = [t for t in targets if t["status"] in {"missing", "stale"}]
    errors = [t for t in targets if t["status"] == "error"]
    return {
        "ok": not needs and not errors,
        "canonical": canonical,
        "targets": targets,
        "needs_action": needs,
        "errors": errors,
        "gh_available": bool(shutil.which("gh")),
    }


def run_gh(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["gh", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def gh_authed() -> bool:
    if not shutil.which("gh"):
        return False
    proc = run_gh(["auth", "status"])
    return proc.returncode == 0


def replace_stale_in_text(text: str, canonical: dict[str, Any], desired: str, match_regex: str) -> str:
    """Replace matched Modellix lines with desired snippet; also rewrite stale URLs elsewhere."""
    pattern = re.compile(match_regex)
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    replaced = False
    for line in lines:
        if pattern.search(line):
            nl = "\n" if line.endswith("\n") else ""
            out.append(desired + nl)
            replaced = True
        else:
            out.append(line)
    body = "".join(out)
    if not replaced and desired:
        # Append near end if somehow matched only via stale elsewhere — keep body, rewrite URLs.
        pass
    for stale in canonical.get("stale_url_substrings") or []:
        if stale in body:
            # Prefer full skill URL when rewriting generic old repo refs in matched contexts.
            body = body.replace(
                "https://github.com/Modellix/modellix-skill/tree/main/modellix-skill",
                canonical["skill_url"],
            )
            body = body.replace(
                "https://github.com/Modellix/modellix-skill",
                canonical["repo_url"],
            )
    return body


def apply_readme_update(target: dict[str, Any], canonical: dict[str, Any], report_item: dict[str, Any]) -> dict[str, Any]:
    if not gh_authed():
        return {
            **report_item,
            "apply_status": "skipped",
            "apply_detail": "gh CLI not installed or not authenticated; run manually",
        }

    repo = target["repo"]
    path = target["path"]
    work = Path(tempfile.mkdtemp(prefix="modellix-listings-"))
    try:
        fork = run_gh(["repo", "fork", repo, "--clone=false", "--default-branch-only"])
        # fork may already exist
        user_proc = run_gh(["api", "user", "-q", ".login"])
        if user_proc.returncode != 0:
            return {**report_item, "apply_status": "error", "apply_detail": user_proc.stderr.strip()}
        user = user_proc.stdout.strip()
        fork_repo = f"{user}/{repo.split('/')[-1]}"
        branch_name = "update-modellix-listing"
        clone = run_gh(
            [
                "repo",
                "clone",
                fork_repo,
                str(work / "repo"),
                "--",
                "--depth",
                "1",
            ]
        )
        if clone.returncode != 0:
            return {**report_item, "apply_status": "error", "apply_detail": clone.stderr.strip() or clone.stdout.strip()}

        repo_dir = work / "repo"
        run_gh(["repo", "sync", fork_repo, "--source", repo, "--force"], cwd=None)
        # Prefer sync via fetch upstream
        subprocess.run(["git", "remote", "add", "upstream", f"https://github.com/{repo}.git"], cwd=repo_dir, capture_output=True)
        subprocess.run(["git", "fetch", "upstream", "--depth", "1"], cwd=repo_dir, capture_output=True)
        default = default_branch(repo)
        subprocess.run(["git", "checkout", "-B", branch_name, f"upstream/{default}"], cwd=repo_dir, capture_output=True)

        file_path = repo_dir / path
        if not file_path.is_file():
            return {**report_item, "apply_status": "error", "apply_detail": f"Missing {path} after clone"}

        original = file_path.read_text(encoding="utf-8")
        desired = target.get("desired_snippet") or ""
        updated = replace_stale_in_text(original, canonical, desired, target.get("match_regex") or "(?i)modellix")
        if updated == original:
            return {**report_item, "apply_status": "noop", "apply_detail": "No text change after rewrite"}

        file_path.write_text(updated, encoding="utf-8")
        subprocess.run(["git", "add", path], cwd=repo_dir, check=False)
        msg = target.get("pr_title") or "Update Modellix listing"
        commit = subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=repo_dir,
            capture_output=True,
            text=True,
        )
        if commit.returncode != 0:
            return {
                **report_item,
                "apply_status": "error",
                "apply_detail": commit.stderr.strip() or commit.stdout.strip() or "commit failed",
            }

        push = subprocess.run(
            ["git", "push", "-u", "origin", branch_name, "--force"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            env={**os.environ, "GIT_HTTP_VERSION": "HTTP/1.1"},
        )
        if push.returncode != 0:
            return {**report_item, "apply_status": "error", "apply_detail": push.stderr.strip() or push.stdout.strip()}

        body = (
            f"Update Modellix listing URLs after the move to `{canonical['repo_url']}`.\n\n"
            f"Canonical skill path: {canonical['skill_url']}\n"
        )
        pr = run_gh(
            [
                "pr",
                "create",
                "--repo",
                repo,
                "--head",
                f"{user}:{branch_name}",
                "--title",
                msg,
                "--body",
                body,
            ],
            cwd=repo_dir,
        )
        if pr.returncode != 0:
            return {**report_item, "apply_status": "error", "apply_detail": pr.stderr.strip() or pr.stdout.strip()}
        return {**report_item, "apply_status": "pr_opened", "pr_url": pr.stdout.strip()}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def apply_updates(config: dict[str, Any], report: dict[str, Any]) -> dict[str, Any]:
    canonical = config["canonical"]
    by_id = {t["id"]: t for t in config["targets"]}
    applied = []
    for item in report["needs_action"]:
        target = by_id.get(item["id"])
        if not target:
            continue
        if item["status"] == "stale" and target["kind"] == "readme_link":
            applied.append(apply_readme_update(target, canonical, item))
        elif target["kind"] == "issue_form":
            applied.append(
                {
                    **item,
                    "apply_status": "manual",
                    "apply_detail": (
                        "Open the External plugin issue form (never PR plugins/external.json). "
                        f"{target.get('issue_url') or ''} Cut a matching release tag + full SHA first. "
                        f"{target.get('notes') or ''}"
                    ),
                    "issue_url": target.get("issue_url"),
                }
            )
        elif item["status"] == "missing":
            applied.append(
                {
                    **item,
                    "apply_status": "manual",
                    "apply_detail": (
                        "First-time listing is not auto-created. Use the desired_snippet / notes in "
                        ".cursor/hooks/community-listings.json and open a PR (English title/body)."
                    ),
                    "desired_snippet": target.get("desired_snippet"),
                }
            )
        elif target["kind"] in {"manual", "vendored_skill", "file_entry"}:
            applied.append(
                {
                    **item,
                    "apply_status": "manual",
                    "apply_detail": target.get("notes") or "Manual PR required",
                    "desired_snippet": target.get("desired_snippet"),
                }
            )
        else:
            applied.append({**item, "apply_status": "skipped", "apply_detail": "No apply handler"})
    report["applied"] = applied
    return report


def format_human(report: dict[str, Any]) -> str:
    lines = ["## Community listing sync", ""]
    lines.append(f"Canonical skill URL: `{report['canonical']['skill_url']}`")
    lines.append(f"`gh` available: {report['gh_available']}")
    lines.append("")
    for t in report["targets"]:
        lines.append(f"- **{t['id']}** (`{t['repo']}`): `{t['status']}` — {t.get('detail') or ''}")
    if report["needs_action"]:
        lines.append("")
        lines.append("### Needs action")
        for t in report["needs_action"]:
            lines.append(f"- {t['id']}: {t['status']} → {t.get('action')} ({t.get('detail')})")
            if t.get("desired_snippet"):
                lines.append(f"  Desired: `{t['desired_snippet']}`")
    if report.get("applied"):
        lines.append("")
        lines.append("### Apply results")
        for t in report["applied"]:
            lines.append(
                f"- {t['id']}: {t.get('apply_status')} — {t.get('pr_url') or t.get('apply_detail') or ''}"
            )
    lines.append("")
    lines.append(
        "Config source of truth: `.cursor/hooks/community-listings.json`. "
        "Apply stale README updates with: `python3 .cursor/hooks/sync_community_listings.py --apply`"
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Read-only status (default)")
    parser.add_argument("--apply", action="store_true", help="Open update PRs for stale readme_link targets")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    parser.add_argument("--write-state", type=Path, help="Write report JSON to this path")
    args = parser.parse_args()
    if not args.apply:
        args.check = True

    config = load_config()
    report = check_all(config)
    if args.apply:
        report = apply_updates(config, report)

    if args.write_state:
        args.write_state.parent.mkdir(parents=True, exist_ok=True)
        args.write_state.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(format_human(report))

    return 0 if report.get("ok") or args.apply else 1


if __name__ == "__main__":
    # Allow importing as module without executing
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        raise SystemExit(0)
