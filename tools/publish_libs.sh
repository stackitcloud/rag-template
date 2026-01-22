#!/usr/bin/env bash
# Shared helpers for publishing internal libs and waiting for index visibility.
set -euo pipefail

POLL_INTERVAL_SECONDS=5
MAX_POLL_ATTEMPTS=60

publish_lib() {
  local lib="$1"
  local repo_flag="$2" # "" or "-r testpypi"
  local version="$3"
  local path="${4:-libs/$lib}"
  if [ ! -d "$path" ]; then
    echo "Missing $path" >&2
    exit 1
  fi
  local pyproject="$path/pyproject.toml"
  if [ -f "$pyproject" ]; then
    python - "$pyproject" "$version" <<'PY'
import re
import sys
from pathlib import Path

pyproject = Path(sys.argv[1])
version = sys.argv[2]
text = pyproject.read_text()
pattern = r'^(\s*rag-core-lib\s*=\s*)\{[^\n]*path\s*=\s*"[^"]+"[^\n]*\}\s*$'
replacement = r'\1"=={}"'.format(version)
new_text = re.sub(pattern, replacement, text, flags=re.M)
if new_text != text:
    pyproject.write_text(new_text)
    print(f"Rewrote rag-core-lib path dependency in {pyproject} to =={version}")
PY
  fi
  # Skip publishing if this version already exists on the target index.
  # This prevents 'poetry publish' from failing when the version is already present.
  if command -v curl >/dev/null 2>&1 && command -v jq >/dev/null 2>&1; then
    local base_url="https://pypi.org"
    if [ "${repo_flag:-}" = "-r testpypi" ]; then
      base_url="https://test.pypi.org"
    fi
    if curl -fsSL "$base_url/pypi/$lib/json" -o /tmp/"$lib".json; then
      if jq -e --arg v "$version" '.releases[$v] | length > 0' /tmp/"$lib".json >/dev/null; then
        echo "$lib==$version already exists on ${repo_flag:-pypi default}; skipping publish"
        return 0
      fi
    fi
  fi
  echo "Publishing $lib ($version) to ${repo_flag:-pypi default}"
  (cd "$path" && poetry version "$version" && poetry build && poetry publish $repo_flag)
}

wait_for_index() {
  local name="$1"
  local version="$2"
  local base_url="$3"
  local label="$4"
  echo "Waiting for $name==$version on $label"
  for _ in $(seq 1 "$MAX_POLL_ATTEMPTS"); do
    json_ok=false
    simple_ok=false
    if curl -fsSL "$base_url/pypi/$name/json" -o /tmp/"$name".json; then
      if jq -e --arg v "$version" '.releases[$v] | length > 0' /tmp/"$name".json >/dev/null; then
        json_ok=true
      fi
    fi
    if curl -fsSL "$base_url/simple/$name/" -o /tmp/"$name".html; then
      if grep -q "$version" /tmp/"$name".html; then
        simple_ok=true
      fi
    fi
    if [ "$json_ok" = true ] && [ "$simple_ok" = true ]; then
      echo "$name==$version visible on $label"
      return 0
    fi
    sleep "$POLL_INTERVAL_SECONDS"
  done
  echo "$name==$version not visible on $label after waiting" >&2
  return 1
}
