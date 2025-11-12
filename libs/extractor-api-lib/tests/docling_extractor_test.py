from pathlib import Path

import pytest

from extractor_api_lib.impl.extractors.file_extractors.docling_extractor import DoclingFileExtractor
from extractor_api_lib.impl.types.content_type import ContentType


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


class _FakeProv:
    def __init__(self, page_no: int):
        self.page_no = page_no


class _FakeTextItem:
    def __init__(self, text: str, page: int):
        self.text = text
        self.prov = [_FakeProv(page)]


class _FakeTableItem:
    def __init__(self, markdown: str, page: int):
        self._markdown = markdown
        self.prov = [_FakeProv(page)]

    def to_markdown(self):
        return self._markdown


class _FakeDocument:
    def __init__(self, items):
        self._items = items

    def iterate_items(self):
        return iter(self._items)


class _FakeConversionResult:
    def __init__(self, document):
        self.document = document


class _FakeConverter:
    def __init__(self, document):
        self._document = document

    def convert(self, _):
        return _FakeConversionResult(self._document)


@pytest.mark.asyncio
async def test_aextract_content_groups_by_page():
    document = _FakeDocument(
        [
            (_FakeTextItem("First page paragraph", page=1), 0),
            (_FakeTableItem("| Col |\n| --- |\n| Value |", page=1), 0),
            (_FakeTextItem("Second page text", page=2), 0),
        ]
    )

    extractor = DoclingFileExtractor.__new__(DoclingFileExtractor)
    extractor._converter = _FakeConverter(document)
    extractor._file_service = None

    pieces = await extractor.aextract_content(Path("dummy"), "sample.pdf")

    assert len(pieces) == 2
    page_one_piece = next(piece for piece in pieces if piece.metadata["page"] == 1)
    assert page_one_piece.type == ContentType.TEXT
    assert page_one_piece.metadata["format"] == "markdown"
    assert "First page paragraph" in page_one_piece.page_content
    assert "| Col |" in page_one_piece.page_content

    page_two_piece = next(piece for piece in pieces if piece.metadata["page"] == 2)
    assert "Second page text" in page_two_piece.page_content


@pytest.mark.asyncio
async def test_dash_only_table_is_dropped():
    document = _FakeDocument(
        [
            (_FakeTableItem("| --- |\n| --- |", page=1), 0),
            (_FakeTextItem("Real content", page=1), 0),
        ]
    )

    extractor = DoclingFileExtractor.__new__(DoclingFileExtractor)
    extractor._converter = _FakeConverter(document)
    extractor._file_service = None

    pieces = await extractor.aextract_content(Path("dummy"), "sample.pdf")

    assert len(pieces) == 1
    content = pieces[0].page_content.strip()
    assert content == "Real content"
    assert "---" not in content
