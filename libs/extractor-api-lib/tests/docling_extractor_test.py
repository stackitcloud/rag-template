from pathlib import Path

import pytest

from extractor_api_lib.impl.extractors.file_extractors.docling_extractor import DoclingFileExtractor
from extractor_api_lib.impl.types.content_type import ContentType


class _FakeDataFrame:
    def __init__(self, markdown: str):
        self._markdown = markdown

    def to_markdown(self, index: bool = False):  # pragma: no cover - simple stub
        return self._markdown


class _FakeTable:
    def __init__(self, markdown: str | None = None, dataframe_markdown: str | None = None, page_no: int = 1):
        self._markdown = markdown
        self._dataframe_markdown = dataframe_markdown
        self.page_no = page_no

    def to_markdown(self):
        if self._markdown is None:
            raise AttributeError  # pragma: no cover - aligns with docling default behaviour when not implemented
        return self._markdown

    def export_to_dataframe(self):
        if self._dataframe_markdown is None:
            raise AttributeError  # pragma: no cover - aligns with docling default behaviour when not implemented
        return _FakeDataFrame(self._dataframe_markdown)


def test_serialize_table_prefers_markdown_attr():
    table = _FakeTable(markdown="| Heading | Value |\n| --- | --- |\n| Entry A | Entry B |")

    extractor = DoclingFileExtractor.__new__(DoclingFileExtractor)
    markdown = extractor._serialize_table(table)

    assert markdown == "| Heading | Value |\n| --- | --- |\n| Entry A | Entry B |"


def test_serialize_table_falls_back_to_dataframe():
    table = _FakeTable(markdown=None, dataframe_markdown="| Col |\n| --- |\n| 42 |")

    extractor = DoclingFileExtractor.__new__(DoclingFileExtractor)
    markdown = extractor._serialize_table(table)

    assert markdown == "| Col |\n| --- |\n| 42 |"


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
        self.pages = [object()]
        self.errors = [object()]
        self.assembled = object()


class _FakeConverter:
    def __init__(self, document):
        self._document = document
        self._conversion_result: _FakeConversionResult | None = None

    def convert(self, _):
        self._conversion_result = _FakeConversionResult(self._document)
        return self._conversion_result


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

    assert len(pieces) == 3

    text_pages = [piece for piece in pieces if piece.type == ContentType.TEXT]
    assert len(text_pages) == 2
    page_one_piece = next(piece for piece in text_pages if piece.metadata["page"] == 1)
    assert "First page paragraph" in page_one_piece.page_content

    page_two_piece = next(piece for piece in text_pages if piece.metadata["page"] == 2)
    assert "Second page text" in page_two_piece.page_content

    table_pieces = [piece for piece in pieces if piece.type == ContentType.TABLE]
    assert len(table_pieces) == 1
    table_piece = table_pieces[0]
    assert table_piece.metadata["table_index"] == 1
    assert "| Col |" in table_piece.page_content


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


@pytest.mark.asyncio
async def test_cleanup_clears_conversion_result_buffers():
    class _DocWithCache(_FakeDocument):
        def __init__(self, items):
            super().__init__(items)
            self.cleared = False

        def _clear_picture_pil_cache(self):  # pragma: no cover - simple flag setter
            self.cleared = True

    document = _DocWithCache([(_FakeTextItem("Content", page=1), 0)])
    converter = _FakeConverter(document)

    extractor = DoclingFileExtractor.__new__(DoclingFileExtractor)
    extractor._converter = converter
    extractor._file_service = None

    await extractor.aextract_content(Path("dummy"), "sample.pdf")

    assert converter._document.cleared is True
    assert converter._conversion_result is not None
    assert converter._conversion_result.pages == []
    assert converter._conversion_result.errors == []
    assert converter._conversion_result.assembled is None
