#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import urllib.request


def main() -> int:
    repo = os.environ.get("GITHUB_REPOSITORY")
    sha = os.environ.get("GITHUB_SHA")
    token = os.environ.get("GH_TOKEN")
    output_path = os.environ.get("GITHUB_OUTPUT")

    if not repo or not sha or not token or not output_path:
        print("Missing required environment variables for chart-bump check.", file=sys.stderr)
        return 1

    url = f"https://api.github.com/repos/{repo}/commits/{sha}/pulls"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.load(resp)
    except Exception as exc:
        print(f"Failed to query PRs for commit: {exc}", file=sys.stderr)
        return 1

    if data:
        labels = {lbl["name"] for lbl in data[0].get("labels", [])}
        allow = "chart-bump" in labels
    else:
        allow = False

    out = f"allow={'true' if allow else 'false'}\n"
    with open(output_path, "a", encoding="utf-8") as handle:
        handle.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
