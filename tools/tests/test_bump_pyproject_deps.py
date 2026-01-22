"""Tests for tools/bump_pyproject_deps.py."""

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
