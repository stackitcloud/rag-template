"""Tests for tools/bump_chart_versions.py."""

from tools.bump_chart_versions import _to_chart_version


def test_to_chart_version_converts_post_suffix() -> None:
    assert _to_chart_version("2.0.0.post20250904105936") == "2.0.0-post.20250904105936"


def test_to_chart_version_keeps_semver_with_prerelease() -> None:
    assert _to_chart_version("v2.0.1-rc.1") == "2.0.1-rc.1"
