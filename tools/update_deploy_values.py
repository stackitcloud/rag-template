#!/usr/bin/env python3
"""Update deployment repo values file with image registry/tag overrides."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict

import yaml


def ensure(mapping: Dict[str, Any], key: str) -> Dict[str, Any]:
    """Ensure key exists and is a dict."""
    if key not in mapping or mapping[key] is None:
        mapping[key] = {}
    if not isinstance(mapping[key], dict):
        raise TypeError(f"Expected dict at {key}, got {type(mapping[key])}")
    return mapping[key]


def update_values(values_path: Path, image_registry: str, image_tag: str) -> None:
    if values_path.exists():
        data = yaml.safe_load(values_path.read_text(encoding="utf-8")) or {}
    else:
        data = {}

    components = {
        "backend": "rag-backend",
        "adminBackend": "admin-backend",
        "extractor": "document-extractor",
        "frontend": "frontend",
        "adminFrontend": "admin-frontend",
    }

    for key, image_name in components.items():
        comp = ensure(data, key)
        image_block = ensure(comp, "image")
        image_block["repository"] = f"{image_registry}/{image_name}"
        image_block["tag"] = image_tag

    backend = ensure(data, "backend")
    mcp = ensure(backend, "mcp")
    mcp_image = ensure(mcp, "image")
    mcp_image["repository"] = f"{image_registry}/mcp-server"
    mcp_image["tag"] = image_tag

    values_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Update image overrides in a values file.")
    parser.add_argument("--values-file", required=True, help="Path to values-qa.yaml in deployment repo")
    parser.add_argument("--image-registry", required=True, help="Image registry base (e.g. registry.onstackit.cloud/qa-rag-template)")
    parser.add_argument("--image-tag", required=True, help="Image tag/version to set")
    args = parser.parse_args()

    update_values(Path(args.values_file), args.image_registry, args.image_tag)


if __name__ == "__main__":
    main()
