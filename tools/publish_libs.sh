#!/usr/bin/env bash
# Shared helpers for publishing internal libs and waiting for index visibility.
set -euo pipefail

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
  echo "Publishing $lib ($version) to ${repo_flag:-pypi default}"
  (cd "$path" && poetry version "$version" && poetry build && poetry publish $repo_flag)
}

wait_for_index() {
  local name="$1"
  local version="$2"
  local base_url="$3"
  local label="$4"
  echo "Waiting for $name==$version on $label"
  for _ in $(seq 1 60); do
    json_ok=false
    simple_ok=false
    if curl -fsSL "$base_url/pypi/$name/json" | jq -e --arg v "$version" '.releases[$v] | length > 0' >/dev/null; then
      json_ok=true
    fi
    if curl -fsSL "$base_url/simple/$name/" | grep -q "$version"; then
      simple_ok=true
    fi
    if [ "$json_ok" = true ] && [ "$simple_ok" = true ]; then
      echo "$name==$version visible on $label"
      return 0
    fi
    sleep 5
  done
  echo "$name==$version not visible on $label after waiting" >&2
  return 1
}
