#!/usr/bin/env python3
import argparse
import pathlib
import sys

import yaml
from packaging.version import Version

ROOT = pathlib.Path(__file__).resolve().parents[1]


def bump_chart(chart_path: pathlib.Path, app_version: str):
    data = yaml.safe_load(chart_path.read_text())
    data['appVersion'] = str(app_version)
    data['version'] = str(app_version)
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
