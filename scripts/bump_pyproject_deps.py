#!/usr/bin/env python3
import argparse
import pathlib
import sys
from typing import Dict, Any

import tomlkit
from tomlkit.items import Table

ROOT = pathlib.Path(__file__).resolve().parents[1]

LIBS = [
    (ROOT / 'libs' / 'rag-core-lib' / 'pyproject.toml', 'tool.poetry.version'),
    (ROOT / 'libs' / 'rag-core-api' / 'pyproject.toml', 'tool.poetry.version'),
    (ROOT / 'libs' / 'admin-api-lib' / 'pyproject.toml', 'tool.poetry.version'),
    (ROOT / 'libs' / 'extractor-api-lib' / 'pyproject.toml', 'tool.poetry.version'),
]

SERVICE_PINS = {
    ROOT / 'services' / 'rag-backend' / 'pyproject.toml': {
        'tool.poetry.group.prod.dependencies.rag-core-api': '=={v}',
        'tool.poetry.group.prod.dependencies.rag-core-lib': '=={v}',
    },
    ROOT / 'services' / 'admin-backend' / 'pyproject.toml': {
        'tool.poetry.group.prod.dependencies.admin-api-lib': '=={v}',
        'tool.poetry.group.prod.dependencies.rag-core-lib': '=={v}',
    },
    ROOT / 'services' / 'document-extractor' / 'pyproject.toml': {
        'tool.poetry.group.prod.dependencies.extractor-api-lib': '=={v}',
    },
}
#


def _ensure_table(parent: Dict[str, Any], key: str) -> Table:
    if key in parent:
        val = parent[key]
        if isinstance(val, Table):
            return val
        # If present but not a Table, replace with a Table (conservative fallback)
    parent[key] = tomlkit.table()
    return parent[key]  # type: ignore[return-value]


def set_value(doc: tomlkit.TOMLDocument, dotted_path: str, value: Any):
    parts = dotted_path.split('.')
    ref: Dict[str, Any] = doc  # tomlkit document behaves like a dict
    for p in parts[:-1]:
        ref = _ensure_table(ref, p)
    ref[parts[-1]] = value


def bump(version: str):
    # 1) bump libs versions
    for file, dotted in LIBS:
        txt = file.read_text()
        doc = tomlkit.parse(txt)
        set_value(doc, dotted, version)
        file.write_text(tomlkit.dumps(doc))
        print(f"Updated {file} -> {dotted} = {version}")

    # 2) bump service pins
    for file, mapping in SERVICE_PINS.items():
        txt = file.read_text()
        doc = tomlkit.parse(txt)
        for dotted, template in mapping.items():
            val = template.format(v=version)
            set_value(doc, dotted, val)
            print(f"Pinned {file} -> {dotted} = {val}")
        file.write_text(tomlkit.dumps(doc))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--version', required=True)
    args = ap.parse_args()
    bump(args.version)


if __name__ == '__main__':
    sys.exit(main())
