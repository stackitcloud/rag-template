#!/usr/bin/env python3
import argparse
import pathlib
import re
import sys
from typing import Dict, Any, List, Optional

import tomlkit
from tomlkit.items import Table

ROOT = pathlib.Path(__file__).resolve().parents[1]

LIBS = [
    ROOT / 'libs' / 'rag-core-lib' / 'pyproject.toml',
    ROOT / 'libs' / 'rag-core-api' / 'pyproject.toml',
    ROOT / 'libs' / 'admin-api-lib' / 'pyproject.toml',
    ROOT / 'libs' / 'extractor-api-lib' / 'pyproject.toml',
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


def replace_version_line(text: str, new_version: str) -> str:
    lines = text.splitlines(keepends=True)
    in_tool_poetry = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('[tool.poetry]'):
            in_tool_poetry = True
            continue
        if in_tool_poetry and stripped.startswith('[') and not stripped.startswith('[tool.poetry]'):
            # left the section without finding version; stop scanning section
            break
        if in_tool_poetry and stripped.startswith('version'):
            # Replace only the version value, keep indentation and spacing
            lines[i] = re.sub(r'version\s*=\s*"[^"]*"', f'version = "{new_version}"', line)
            return ''.join(lines)
    # If no version line found, append it to the [tool.poetry] section
    out = ''.join(lines)
    return out + f"\n[tool.poetry]\nversion = \"{new_version}\"\n"


def _get_table(doc: tomlkit.TOMLDocument, path: List[str]) -> Optional[Table]:
    ref: Any = doc
    for key in path:
        if not isinstance(ref, (tomlkit.TOMLDocument, Table)) or key not in ref:
            return None
        ref = ref[key]
    return ref if isinstance(ref, Table) else None


def bump(version: str):
    # 1) bump libs versions (textual, non-destructive)
    for file in LIBS:
        txt = file.read_text()
        new_txt = replace_version_line(txt, version)
        file.write_text(new_txt)
        print(f"Updated {file} -> tool.poetry.version = {version}")

    # 2) bump service pins only inside [tool.poetry.group.prod.dependencies]
    for file, mapping in SERVICE_PINS.items():
        txt = file.read_text()
        doc = tomlkit.parse(txt)
        deps = _get_table(doc, [
            'tool', 'poetry', 'group', 'prod', 'dependencies'
        ])
        if deps is None:
            print(f"Skip {file}: prod dependencies table not found")
            continue
        for dotted, template in mapping.items():
            pkg = dotted.split('.')[-1]
            if pkg in deps:
                val = template.format(v=version)
                deps[pkg] = val
                print(f"Pinned {file} -> {pkg} = {val}")
            else:
                print(f"Skip {file}: {pkg} not present in prod dependencies")
        file.write_text(tomlkit.dumps(doc))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--version', required=True)
    args = ap.parse_args()
    bump(args.version)


if __name__ == '__main__':
    sys.exit(main())
