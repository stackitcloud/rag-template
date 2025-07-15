#!/usr/bin/env python3
"""
Update Helm values.yaml with new version tags for specific services only,
preserving all existing formatting and disabling line wrapping via ruamel.yaml.
"""

import sys
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import DoubleQuotedScalarString

def update_helm_values(file_path, new_version):
    """Update specific service image tags in values.yaml with ruamel.yaml."""
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = float('inf')           # ← no wrapping, even for long lines
    yaml.indent(mapping=2, sequence=4, offset=2)

    with open(file_path, 'r') as f:
        data = yaml.load(f)

    services_to_update = [
        ('backend', 'mcp', 'image', 'tag'),
        ('backend', 'image', 'tag'),
        ('frontend', 'image', 'tag'),
        ('adminBackend', 'image', 'tag'),
        ('extractor', 'image', 'tag'),
        ('adminFrontend', 'image', 'tag'),
    ]

    new_tag = f"v{new_version}"
    updated_count = 0

    for path in services_to_update:
        node = data
        try:
            for key in path[:-1]:
                node = node[key]
            tag_key = path[-1]
            if tag_key in node:
                old = node[tag_key]
                if str(old) != new_tag:
                    if hasattr(old, 'style') and old.style in ('"', "'"):
                        node[tag_key] = DoubleQuotedScalarString(new_tag)
                    else:
                        node[tag_key] = new_tag
                    print(f"✅ Updated {'.'.join(path)}: {old!r} → {new_tag!r}")
                    updated_count += 1
                else:
                    print(f"⚠️  {'.'.join(path)} already at {new_tag!r}")
            else:
                print(f"❌ Could not find {'.'.join(path)}")
        except (KeyError, TypeError) as e:
            print(f"❌ Could not access {'.'.join(path)}: {e}")

    if updated_count:
        with open(file_path, 'w') as f:
            yaml.dump(data, f)
        print(f"\n✅ Updated {updated_count} tag(s) in {file_path}")
        return True
    else:
        print(f"\n⚠️  No changes needed in {file_path}")
        return False

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: update-helm-values.py <version>")
        sys.exit(1)

    version = sys.argv[1]
    file_path = 'infrastructure/rag/values.yaml'
    success = update_helm_values(file_path, version)
    sys.exit(0 if success else 1)
