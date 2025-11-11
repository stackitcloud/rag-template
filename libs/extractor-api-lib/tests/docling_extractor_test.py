import pytest

from extractor_api_lib.impl.extractors.file_extractors.docling_extractor import DoclingFileExtractor


class _FakeCell:
    def __init__(self, repr_text: str):
        self._repr_text = repr_text

    def __str__(self) -> str:  # pragma: no cover - simple data holder
        return self._repr_text


class _FakeRow:
    def __init__(self, cells):
        self.cells = cells


class _FakeTable:
    def __init__(self, rows):
        self.rows = rows
        self.page_no = 1


class _FragmentCell:
    def __init__(self, fragments):
        self.text = fragments


class _GetTextCell:
    def __init__(self, value: str):
        self._value = value

    def get_text(self):
        return self._value


def test_serialize_table_extracts_text_from_repr():
    table = _FakeTable(
        rows=[
            _FakeRow(
                [
                    _FakeCell(
                        "text='Heading' column_header=True bbox=BoundingBox(l=0, t=0, r=1, b=1)"
                    ),
                    _FakeCell(
                        "text='Value' column_header=True bbox=BoundingBox(l=1, t=0, r=2, b=1)"
                    ),
                ]
            ),
            _FakeRow(
                [
                    _FakeCell(
                        "text='Entry A' column_header=False bbox=BoundingBox(l=0, t=1, r=1, b=2)"
                    ),
                    _FakeCell(
                        "text='Entry B' column_header=False bbox=BoundingBox(l=1, t=1, r=2, b=2)"
                    ),
                ]
            ),
        ]
    )

    extractor = DoclingFileExtractor.__new__(DoclingFileExtractor)
    markdown = extractor._serialize_table(table)

    assert markdown == "| Heading | Value |\n| --- | --- |\n| Entry A | Entry B |"


@pytest.mark.parametrize(
    "cells, expected",
    [
        ([ _FragmentCell(["Part", "One"]) ], "Part One"),
        ([ _GetTextCell("From getter") ], "From getter"),
    ],
)
def test_cell_to_text_handles_various_sources(cells, expected):
    row = _FakeRow(cells)
    table = _FakeTable([row])

    extractor = DoclingFileExtractor.__new__(DoclingFileExtractor)
    result = extractor._serialize_table(table)

    assert expected in result
