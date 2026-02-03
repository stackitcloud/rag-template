"""Tests for tools/bump_pyproject_deps.py."""

from pathlib import Path

import tomlkit

from tools import bump_pyproject_deps
from tools.bump_pyproject_deps import replace_version_line


def test_replace_version_line_updates_existing_version() -> None:
    text = (
        "[tool.poetry]\n"
        "name = \"example\"\n"
        "version = \"0.1.0\"\n"
        "\n"
        "[tool.poetry.dependencies]\n"
        "python = \"^3.13\"\n"
    )

    out = replace_version_line(text, "1.2.3")

    assert "version = \"1.2.3\"" in out
    assert out.count("[tool.poetry]") == 1


def test_replace_version_line_inserts_version_without_duplicate_section() -> None:
    text = (
        "[tool.poetry]\n"
        "name = \"example\"\n"
        "\n"
        "[tool.poetry.dependencies]\n"
        "python = \"^3.13\"\n"
    )

    out = replace_version_line(text, "2.0.0")

    assert "version = \"2.0.0\"" in out
    assert out.count("[tool.poetry]") == 1


def _write_pyproject(path: Path, name: str, version: str, with_rag_core_dep: bool) -> None:
    lines = [
        "[tool.poetry]",
        f"name = \"{name}\"",
        f"version = \"{version}\"",
        "",
        "[tool.poetry.dependencies]",
        "python = \"^3.13\"",
    ]
    if with_rag_core_dep:
        lines.append("rag-core-lib = \"==4.0.0\"")
    path.write_text("\n".join(lines) + "\n")


def test_bump_updates_internal_lib_dependency_pins(tmp_path: Path, monkeypatch) -> None:
    rag_core_lib = tmp_path / "rag-core-lib.toml"
    rag_core_api = tmp_path / "rag-core-api.toml"
    admin_api_lib = tmp_path / "admin-api-lib.toml"
    extractor_api_lib = tmp_path / "extractor-api-lib.toml"

    _write_pyproject(rag_core_lib, "rag-core-lib", "4.0.0", with_rag_core_dep=False)
    _write_pyproject(rag_core_api, "rag-core-api", "4.0.0", with_rag_core_dep=True)
    _write_pyproject(admin_api_lib, "admin-api-lib", "4.0.0", with_rag_core_dep=True)
    _write_pyproject(extractor_api_lib, "extractor-api-lib", "4.0.0", with_rag_core_dep=True)

    monkeypatch.setattr(
        bump_pyproject_deps,
        "LIBS_VERSION_FILES",
        [rag_core_lib, rag_core_api, admin_api_lib, extractor_api_lib],
    )
    monkeypatch.setattr(
        bump_pyproject_deps,
        "LIB_DEP_PINS",
        {
            rag_core_api: {"tool.poetry.dependencies.rag-core-lib": "=={v}"},
            admin_api_lib: {"tool.poetry.dependencies.rag-core-lib": "=={v}"},
            extractor_api_lib: {"tool.poetry.dependencies.rag-core-lib": "=={v}"},
        },
    )

    bump_pyproject_deps.bump("4.1.0", bump_libs=True, bump_service_pins=False)

    rag_core_doc = tomlkit.parse(rag_core_lib.read_text())
    rag_core_api_doc = tomlkit.parse(rag_core_api.read_text())
    admin_api_doc = tomlkit.parse(admin_api_lib.read_text())
    extractor_api_doc = tomlkit.parse(extractor_api_lib.read_text())

    assert rag_core_doc["tool"]["poetry"]["version"] == "4.1.0"
    assert rag_core_api_doc["tool"]["poetry"]["version"] == "4.1.0"
    assert admin_api_doc["tool"]["poetry"]["version"] == "4.1.0"
    assert extractor_api_doc["tool"]["poetry"]["version"] == "4.1.0"

    assert rag_core_api_doc["tool"]["poetry"]["dependencies"]["rag-core-lib"] == "==4.1.0"
    assert admin_api_doc["tool"]["poetry"]["dependencies"]["rag-core-lib"] == "==4.1.0"
    assert extractor_api_doc["tool"]["poetry"]["dependencies"]["rag-core-lib"] == "==4.1.0"


def test_bump_updates_service_pins(tmp_path: Path, monkeypatch) -> None:
    service_pyproject = tmp_path / "document-extractor.toml"
    service_pyproject.write_text(
        "\n".join(
            [
                "[tool.poetry]",
                "name = \"extractor-server\"",
                "version = \"0.1.0\"",
                "",
                "[tool.poetry.group.prod.dependencies]",
                "extractor-api-lib = \"==4.0.0\"",
                "rag-core-lib = \"==4.0.0\"",
                "",
            ]
        )
        + "\n"
    )

    monkeypatch.setattr(
        bump_pyproject_deps,
        "SERVICE_PINS",
        {
            service_pyproject: {
                "tool.poetry.group.prod.dependencies.extractor-api-lib": "=={v}",
                "tool.poetry.group.prod.dependencies.rag-core-lib": "=={v}",
            }
        },
    )

    bump_pyproject_deps.bump("4.1.0", bump_libs=False, bump_service_pins=True)

    doc = tomlkit.parse(service_pyproject.read_text())
    deps = doc["tool"]["poetry"]["group"]["prod"]["dependencies"]

    assert deps["extractor-api-lib"] == "==4.1.0"
    assert deps["rag-core-lib"] == "==4.1.0"
