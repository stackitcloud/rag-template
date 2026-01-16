#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import tomlkit


REPO_ROOT = Path(__file__).resolve().parents[1]
INTERNAL_LIBS = {
    "rag-core-lib",
    "rag-core-api",
    "admin-api-lib",
    "extractor-api-lib",
}
LIB_PYPROJECTS = [
    REPO_ROOT / "libs" / "rag-core-lib" / "pyproject.toml",
    REPO_ROOT / "libs" / "rag-core-api" / "pyproject.toml",
    REPO_ROOT / "libs" / "admin-api-lib" / "pyproject.toml",
    REPO_ROOT / "libs" / "extractor-api-lib" / "pyproject.toml",
]


def get_table(doc: tomlkit.TOMLDocument, path: list[str]):
    ref = doc
    for key in path:
        if key not in ref:
            return None
        ref = ref[key]
    return ref


def ensure_testpypi_source(pyproject: Path) -> None:
    if not pyproject.exists():
        return

    doc = tomlkit.parse(pyproject.read_text())
    tool = doc.get("tool") or tomlkit.table()
    poetry = tool.get("poetry") or tomlkit.table()
    sources = poetry.get("source")
    if sources is None:
        sources = tomlkit.aot()
        poetry["source"] = sources

    changed = False
    has_testpypi = any(src.get("name") == "testpypi" for src in sources)
    if not has_testpypi:
        src = tomlkit.table()
        src.add("name", "testpypi")
        src.add("url", "https://test.pypi.org/simple/")
        src.add("priority", "supplemental")
        sources.append(src)
        changed = True

    deps = get_table(doc, ["tool", "poetry", "dependencies"])
    if deps is not None:
        for name in INTERNAL_LIBS:
            if name not in deps:
                continue
            val = deps[name]
            if isinstance(val, str):
                it = tomlkit.inline_table()
                it.add("version", val)
                it.add("source", "testpypi")
                deps[name] = it
                changed = True
            elif hasattr(val, "get"):
                if "path" in val:
                    continue
                val["source"] = "testpypi"
                changed = True

    tool["poetry"] = poetry
    doc["tool"] = tool
    if changed:
        pyproject.write_text(tomlkit.dumps(doc))


def main() -> int:
    for pyproject in LIB_PYPROJECTS:
        ensure_testpypi_source(pyproject)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
