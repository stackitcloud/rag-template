#!/usr/bin/env python3
"""Bump internal library versions and update service dependency pins.

This script is used by GitHub Actions release automation.
"""

import argparse
import pathlib
import sys
from typing import Any

import tomlkit

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Only bump versions for internal libs here
LIBS_VERSION_FILES = [
    ROOT / 'libs' / 'rag-core-lib' / 'pyproject.toml',
    ROOT / 'libs' / 'rag-core-api' / 'pyproject.toml',
    ROOT / 'libs' / 'admin-api-lib' / 'pyproject.toml',
    ROOT / 'libs' / 'extractor-api-lib' / 'pyproject.toml',
]

# Internal library dependency pins to keep in sync with lib versions
LIB_DEP_PINS = {
    ROOT / 'libs' / 'rag-core-api' / 'pyproject.toml': {
        'tool.poetry.dependencies.rag-core-lib': '=={v}',
    },
    ROOT / 'libs' / 'admin-api-lib' / 'pyproject.toml': {
        'tool.poetry.dependencies.rag-core-lib': '=={v}',
    },
    ROOT / 'libs' / 'extractor-api-lib' / 'pyproject.toml': {
        'tool.poetry.dependencies.rag-core-lib': '=={v}',
    },
}

# Service pins to update after libs are published
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
    """Set tool.poetry.version in a pyproject.toml text.

    Parameters
    ----------
    text : str
        TOML document text.
    new_version : str
        Version to write into `[tool.poetry]`.

    Returns
    -------
    str
        Updated TOML text.
    """
    doc = tomlkit.parse(text)
    tool = doc.get("tool")
    if tool is None:
        doc["tool"] = tomlkit.table()
        tool = doc["tool"]
    poetry = tool.get("poetry")
    if poetry is None:
        tool["poetry"] = tomlkit.table()
        poetry = tool["poetry"]
    poetry["version"] = str(new_version)
    return tomlkit.dumps(doc)


def _get_table(doc: tomlkit.TOMLDocument, path: list[str]) -> Any | None:
    ref: Any = doc
    for key in path:
        try:
            if key not in ref:  # mapping-like check
                return None
            ref = ref[key]
        except Exception:
            return None
    return ref


def bump(version: str, bump_libs: bool = True, bump_service_pins: bool = True) -> None:
    # 1) bump libs versions (textual, non-destructive)
    if bump_libs:
        for file in LIBS_VERSION_FILES:
            txt = file.read_text()
            new_txt = replace_version_line(txt, version)
            file.write_text(new_txt)
            print(f"Updated {file} -> tool.poetry.version = {version}")

        # Keep internal lib dependency pins aligned with the bumped version.
        for file, mapping in LIB_DEP_PINS.items():
            txt = file.read_text()
            doc = tomlkit.parse(txt)
            deps = _get_table(doc, [
                'tool', 'poetry', 'dependencies'
            ])
            if deps is None or not hasattr(deps, '__contains__'):
                print(f"Skip {file}: dependencies table not found")
                file.write_text(tomlkit.dumps(doc))
                continue
            for dotted, template in mapping.items():
                pkg = dotted.split('.')[-1]
                if pkg in deps:
                    val = template.format(v=version)
                    deps[pkg] = val
                    print(f"Pinned {file} -> {pkg} = {val}")
                else:
                    print(f"Skip {file}: {pkg} not present in dependencies")
            file.write_text(tomlkit.dumps(doc))

    # 2) bump service pins only inside [tool.poetry.group.prod.dependencies]
    if bump_service_pins:
        for file, mapping in SERVICE_PINS.items():
            txt = file.read_text()
            doc = tomlkit.parse(txt)
            deps = _get_table(doc, [
                'tool', 'poetry', 'group', 'prod', 'dependencies'
            ])
            if deps is None or not hasattr(deps, '__contains__'):
                print(f"Skip {file}: prod dependencies table not found")
                file.write_text(tomlkit.dumps(doc))
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", required=True)
    ap.add_argument("--bump-libs", action="store_true", help="Bump versions in internal libs only")
    ap.add_argument("--bump-service-pins", action="store_true", help="Bump service dependency pins only")
    args = ap.parse_args()

    # Backward compatibility: if neither flag is provided, do both
    bump_libs = args.bump_libs or (not args.bump_libs and not args.bump_service_pins)
    bump_service_pins = args.bump_service_pins or (not args.bump_libs and not args.bump_service_pins)

    bump(args.version, bump_libs=bump_libs, bump_service_pins=bump_service_pins)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
