#!/usr/bin/env python3
"""Ensure internal libs depend on rag-core-lib from the TestPyPI source.

This helper is used by CI workflows when building lockfiles in a dry-run mode
against TestPyPI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

import tomlkit
from tomlkit.items import InlineTable, Table


REPO_ROOT = Path(__file__).resolve().parents[1]
LIB_PYPROJECTS = [
    REPO_ROOT / "libs" / "rag-core-lib" / "pyproject.toml",
    REPO_ROOT / "libs" / "rag-core-api" / "pyproject.toml",
    REPO_ROOT / "libs" / "admin-api-lib" / "pyproject.toml",
    REPO_ROOT / "libs" / "extractor-api-lib" / "pyproject.toml",
]
RAG_CORE_LIB = "rag-core-lib"


def get_dependencies(doc: tomlkit.TOMLDocument) -> Table | None:
    """Return `[tool.poetry.dependencies]` table if present.

    Parameters
    ----------
    doc : tomlkit.TOMLDocument
        Parsed TOML document.

    Returns
    -------
    tomlkit.items.Table | None
        Dependencies table or None if the path doesn't exist.
    """
    ref: object = doc
    for key in ["tool", "poetry", "dependencies"]:
        if not isinstance(ref, Mapping) or key not in ref:
            return None
        ref = ref[key]
    return ref if isinstance(ref, Table) else None


def set_rag_core_lib_source(pyproject: Path) -> bool:
    """Set `rag-core-lib` dependency to use the TestPyPI source.

    Parameters
    ----------
    pyproject : pathlib.Path
        Path to a pyproject.toml.

    Returns
    -------
    bool
        True if the file was updated, False if nothing was changed.
    """
    if not pyproject.exists():
        return False

    doc = tomlkit.parse(pyproject.read_text())
    deps = get_dependencies(doc)
    if deps is None or RAG_CORE_LIB not in deps:
        return False

    val = deps[RAG_CORE_LIB]
    if isinstance(val, str):
        it: InlineTable = tomlkit.inline_table()
        it.add("version", val)
        it.add("source", "testpypi")
        deps[RAG_CORE_LIB] = it
    elif hasattr(val, "get"):
        if "path" in val:
            return False
        val["source"] = "testpypi"
    else:
        return False

    doc["tool"]["poetry"]["dependencies"] = deps
    pyproject.write_text(tomlkit.dumps(doc))
    return True


def main() -> int:
    """Update all internal lib pyproject files.

    Returns
    -------
    int
        Process exit code.
    """
    for pyproject in LIB_PYPROJECTS:
        set_rag_core_lib_source(pyproject)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
