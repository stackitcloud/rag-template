#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import tomlkit


REPO_ROOT = Path(__file__).resolve().parents[1]
LIB_PYPROJECTS = [
    REPO_ROOT / "libs" / "rag-core-lib" / "pyproject.toml",
    REPO_ROOT / "libs" / "rag-core-api" / "pyproject.toml",
    REPO_ROOT / "libs" / "admin-api-lib" / "pyproject.toml",
    REPO_ROOT / "libs" / "extractor-api-lib" / "pyproject.toml",
]
RAG_CORE_LIB = "rag-core-lib"


def get_dependencies(doc: tomlkit.TOMLDocument):
    ref = doc
    for key in ["tool", "poetry", "dependencies"]:
        if key not in ref:
            return None
        ref = ref[key]
    return ref


def set_rag_core_lib_source(pyproject: Path) -> bool:
    if not pyproject.exists():
        return False

    doc = tomlkit.parse(pyproject.read_text())
    deps = get_dependencies(doc)
    if deps is None or RAG_CORE_LIB not in deps:
        return False

    val = deps[RAG_CORE_LIB]
    if isinstance(val, str):
        it = tomlkit.inline_table()
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
    for pyproject in LIB_PYPROJECTS:
        set_rag_core_lib_source(pyproject)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
