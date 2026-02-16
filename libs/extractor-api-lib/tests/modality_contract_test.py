"""Contract tests for modality metadata consistency across extraction paths."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest


CONTRACT_DIR = Path(__file__).parent / "test_data" / "modality_contract"
ALLOWED_MODALITIES = {"TEXT", "TABLE", "IMAGE"}


def _load_fixture(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _validate_piece(piece: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    modality = piece.get("type")
    metadata = piece.get("metadata")
    page_content = piece.get("page_content")

    if modality not in ALLOWED_MODALITIES:
        errors.append("type must be one of TEXT/TABLE/IMAGE")

    if not isinstance(page_content, str):
        errors.append("page_content must be a string")

    if not isinstance(metadata, dict):
        errors.append("metadata must be an object")
        return errors

    required_common = ("document", "page", "id", "related")
    for key in required_common:
        if key not in metadata:
            errors.append(f'metadata missing required key: "{key}"')

    if "related" in metadata and not isinstance(metadata.get("related"), list):
        errors.append('metadata["related"] must be a list')

    if modality == "IMAGE":
        has_legacy = bool(metadata.get("base64_image"))
        has_image_url = bool(metadata.get("image_url"))
        has_image_ref = bool(metadata.get("image_ref"))
        has_reference = has_image_url or has_image_ref

        if not (has_legacy or has_reference):
            errors.append("IMAGE metadata must contain base64_image or image_url/image_ref")

        if has_reference and not metadata.get("image_mime"):
            errors.append("IMAGE metadata with image_url/image_ref must include image_mime")

    return errors


@pytest.mark.parametrize(
    "fixture_path",
    sorted(CONTRACT_DIR.glob("*.json")),
    ids=lambda p: p.stem,
)
def test_modality_contract_fixture(fixture_path: Path):
    """Validate every contract fixture against the shared modality schema."""
    fixture = _load_fixture(fixture_path)
    piece = fixture["piece"]
    valid = bool(fixture["valid"])

    errors = _validate_piece(piece)

    if valid:
        assert errors == [], f"Fixture {fixture_path.name} failed contract checks: {errors}"
    else:
        assert errors, f"Fixture {fixture_path.name} was expected to fail but passed."


def test_modality_contract_fixture_names_are_unique():
    """Ensure fixture names stay unique for clear test diagnostics."""
    fixtures = [_load_fixture(path) for path in sorted(CONTRACT_DIR.glob("*.json"))]
    names = [fixture.get("name") for fixture in fixtures]
    assert len(names) == len(set(names))
