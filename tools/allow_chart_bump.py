#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request


API_VERSION = "2022-11-28"


def github_request(url: str, token: str, accept: str | None = None):
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", accept or "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", API_VERSION)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def parse_pr_number(event_path: str | None) -> int | None:
    if not event_path or not os.path.exists(event_path):
        return None
    with open(event_path, "r", encoding="utf-8") as handle:
        event = json.load(handle)

    if "pull_request" in event:
        return event["pull_request"].get("number")

    messages: list[str] = []
    head = event.get("head_commit", {})
    if head.get("message"):
        messages.append(head["message"])
    for commit in event.get("commits", []):
        if commit.get("message"):
            messages.append(commit["message"])

    for msg in messages:
        match = re.search(r"Merge pull request #(\d+)", msg)
        if match:
            return int(match.group(1))
        match = re.search(r"\(#(\d+)\)\s*$", msg)
        if match:
            return int(match.group(1))
    return None


def pr_has_chart_bump(repo: str, pr_number: int, token: str) -> bool:
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}"
    data = github_request(url, token)
    labels = {lbl["name"] for lbl in data.get("labels", [])}
    return "chart-bump" in labels


def find_pr_by_commit(repo: str, sha: str, token: str) -> int | None:
    url = f"https://api.github.com/repos/{repo}/commits/{sha}/pulls"
    data = github_request(
        url,
        token,
        accept="application/vnd.github+json, application/vnd.github.groot-preview+json",
    )
    if data:
        return data[0].get("number")
    return None


def find_pr_by_merge_sha(repo: str, sha: str, token: str) -> int | None:
    for page in range(1, 4):
        url = (
            f"https://api.github.com/repos/{repo}/pulls"
            f"?state=closed&sort=updated&direction=desc&per_page=100&page={page}"
        )
        data = github_request(url, token)
        for pr in data:
            if pr.get("merge_commit_sha") == sha:
                return pr.get("number")
        if len(data) < 100:
            break
    return None


def main() -> int:
    repo = os.environ.get("GITHUB_REPOSITORY")
    sha = os.environ.get("GITHUB_SHA")
    token = os.environ.get("GH_TOKEN")
    output_path = os.environ.get("GITHUB_OUTPUT")
    event_path = os.environ.get("GITHUB_EVENT_PATH")

    if not repo or not sha or not token or not output_path:
        print("Missing required environment variables for chart-bump check.", file=sys.stderr)
        return 1

    try:
        pr_number = parse_pr_number(event_path)
        if pr_number is None:
            pr_number = find_pr_by_commit(repo, sha, token)
        if pr_number is None:
            pr_number = find_pr_by_merge_sha(repo, sha, token)
        if pr_number is None:
            allow = False
        else:
            allow = pr_has_chart_bump(repo, pr_number, token)
    except Exception as exc:
        print(f"Failed to query PRs for commit: {exc}", file=sys.stderr)
        return 1

    out = f"allow={'true' if allow else 'false'}\n"
    with open(output_path, "a", encoding="utf-8") as handle:
        handle.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
