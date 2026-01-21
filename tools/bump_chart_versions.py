#!/usr/bin/env python3
"""Bump Helm chart versions.

This helper updates `Chart.yaml` files under `infrastructure/*/Chart.yaml`.
It preserves quoting style where possible.
"""

import argparse
import pathlib
import re
import sys
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import DoubleQuotedScalarString, SingleQuotedScalarString

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _to_chart_version(app_version: str) -> str:
    """Convert app_version to a SemVer 2.0.0 compliant Helm chart version.

    Examples:
    - "2.0.0.post20250904105936" -> "2.0.0-post.20250904105936"
    - "2.0.1" -> "2.0.1"
    - "2.0.1-rc.1" -> "2.0.1-rc.1"
    - Fallback: if an unexpected format is provided, try to keep a valid semver
      by extracting the leading MAJOR.MINOR.PATCH.
    """
    normalized = app_version.lstrip("vV")
    # Case 1: our prepare-release format "X.Y.Z.post<digits>"
    m = re.fullmatch(r"(?P<base>\d+\.\d+\.\d+)\.post(?P<ts>\d+)", normalized)
    if m:
        return f"{m.group('base')}-post.{m.group('ts')}"

    # Case 2: already valid semver (optionally with pre-release or build metadata)
    if re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?", normalized):
        return normalized

    # Fallback: keep only the base version if present
    base = re.match(r"(\d+\.\d+\.\d+)", normalized)
    return base.group(1) if base else normalized


def _preserve_style(old_value: Any, new_value: str) -> Any:
    if isinstance(old_value, DoubleQuotedScalarString):
        return DoubleQuotedScalarString(new_value)
    if isinstance(old_value, SingleQuotedScalarString):
        return SingleQuotedScalarString(new_value)
    return new_value


def bump_chart(chart_path: pathlib.Path, app_version: str, mode: str) -> None:
    """Update a Chart.yaml file.

    Parameters
    ----------
    chart_path : pathlib.Path
        Path to Chart.yaml.
    app_version : str
        Version string used as input. Depending on mode, this is used to set
        `appVersion` and/or compute the chart `version`.
    mode : str
        One of: "app-and-chart", "app-only", "chart-only".
    """
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 4096

    try:
        data = yaml.load(chart_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Failed to parse YAML from {chart_path}: {exc}") from exc
    if data is None:
        return

    if mode in ("app-and-chart", "app-only"):
        if not app_version:
            raise ValueError("app_version is required for mode app-and-chart or app-only")
        old_app = data.get("appVersion")
        data["appVersion"] = _preserve_style(old_app, str(app_version))

    if mode in ("app-and-chart", "chart-only"):
        if mode == "chart-only" and not app_version:
            raise ValueError("chart-only mode requires chart_version provided via app_version argument")
        chart_version = _to_chart_version(str(app_version))
        old_version = data.get("version")
        data["version"] = _preserve_style(old_version, chart_version)

    try:
        with chart_path.open("w", encoding="utf-8") as handle:
            yaml.dump(data, handle)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Failed to write YAML to {chart_path}: {exc}") from exc


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--app-version", help="App version to set (required for app-and-chart/app-only)")
    p.add_argument("--chart-version", help="Chart version to set (required for chart-only)")
    p.add_argument(
        "--mode",
        choices=["app-and-chart", "app-only", "chart-only"],
        default="app-and-chart",
        help=(
            "app-and-chart: bump appVersion and chart version; "
            "app-only: bump only appVersion; "
            "chart-only: bump only chart version"
        ),
    )
    args = p.parse_args()

    app_version = args.app_version
    if args.mode == "chart-only":
        app_version = args.chart_version

    charts = list((ROOT / "infrastructure").glob("*/Chart.yaml"))
    try:
        for ch in charts:
            bump_chart(ch, app_version, args.mode)
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
