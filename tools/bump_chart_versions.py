#!/usr/bin/env python3
import argparse
import pathlib
import sys
import re

import yaml

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
    # Case 1: our prepare-release format "X.Y.Z.post<digits>"
    m = re.fullmatch(r"(?P<base>\d+\.\d+\.\d+)\.post(?P<ts>\d+)", app_version)
    if m:
        return f"{m.group('base')}-post.{m.group('ts')}"

    # Case 2: already valid semver (optionally with pre-release or build metadata)
    if re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?", app_version):
        return app_version

    # Fallback: keep only the base version if present
    base = re.match(r"(\d+\.\d+\.\d+)", app_version)
    return base.group(1) if base else app_version


def bump_chart(chart_path: pathlib.Path, app_version: str):
    data = yaml.safe_load(chart_path.read_text())
    data['appVersion'] = str(app_version)
    data['version'] = _to_chart_version(str(app_version))
    chart_path.write_text(yaml.safe_dump(data, sort_keys=False))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--app-version', required=True)
    args = p.parse_args()

    charts = list((ROOT / 'infrastructure').glob('*/Chart.yaml'))
    for ch in charts:
        bump_chart(ch, args.app_version)


if __name__ == '__main__':
    sys.exit(main())
