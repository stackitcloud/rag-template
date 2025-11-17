from pathlib import Path

import pytest

from extractor_api_lib.impl.extractors.file_extractors import docling_extractor as docling_module
from extractor_api_lib.impl.extractors.file_extractors.docling_extractor import DoclingFileExtractor
from extractor_api_lib.impl.types.content_type import ContentType
from extractor_api_lib.file_services.file_service import FileService


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

    def export_to_markdown(self):
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


class _NoopFileService(FileService):
    def download_folder(self, source: str, target: Path) -> None:  # pragma: no cover - not used in tests
        raise NotImplementedError

    def download_file(self, source: str, target_file) -> None:  # pragma: no cover - not used in tests
        raise NotImplementedError

    def upload_file(self, file_path: str, file_name: str) -> None:  # pragma: no cover - not used in tests
        raise NotImplementedError

    def get_all_sorted_file_names(self) -> list[str]:  # pragma: no cover - not used in tests
        raise NotImplementedError

    def delete_file(self, file_name: str) -> None:  # pragma: no cover - not used in tests
        raise NotImplementedError


DATA_DIR = Path(__file__).parent / "test_data"


@pytest.mark.asyncio
async def test_aextract_content_groups_by_page(monkeypatch: pytest.MonkeyPatch):
    document = _FakeDocument(
        [
            (_FakeTextItem("First page paragraph", page=1), 0),
            (_FakeTableItem("| Col |\n| --- |\n| Value |", page=1), 0),
            (_FakeTextItem("Second page text", page=2), 0),
        ]
    )

    monkeypatch.setattr(docling_module, "TextItem", _FakeTextItem)
    monkeypatch.setattr(docling_module, "TableItem", _FakeTableItem)

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
async def test_dash_only_table_is_dropped(monkeypatch: pytest.MonkeyPatch):
    document = _FakeDocument(
        [
            (_FakeTableItem("| --- |\n| --- |", page=1), 0),
            (_FakeTextItem("Real content", page=1), 0),
        ]
    )

    monkeypatch.setattr(docling_module, "TextItem", _FakeTextItem)
    monkeypatch.setattr(docling_module, "TableItem", _FakeTableItem)

    extractor = DoclingFileExtractor.__new__(DoclingFileExtractor)
    extractor._converter = _FakeConverter(document)
    extractor._file_service = None

    pieces = await extractor.aextract_content(Path("dummy"), "sample.pdf")

    assert len(pieces) == 1
    content = pieces[0].page_content.strip()
    assert content == "Real content"
    assert "---" not in content


@pytest.mark.asyncio
async def test_docling_extracts_real_html_document():
    sample_file = DATA_DIR / "sample.html"
    extractor = DoclingFileExtractor(_NoopFileService())

    pieces = await extractor.aextract_content(sample_file, sample_file.name)

    assert pieces, "Docling should return at least one information piece"

    text_piece = next(piece for piece in pieces if piece.type == ContentType.TEXT)
    assert "Docling Sample Document" in text_piece.page_content
    assert "Trailing text" in text_piece.page_content

    table_piece = next(piece for piece in pieces if piece.type == ContentType.TABLE)
    assert "Alpha" in table_piece.page_content and "Beta" in table_piece.page_content
    assert table_piece.metadata["origin_extractor"] == "docling"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "relative_path",
    [
        "mixed_content_document.pdf",
        "text_based_document.pdf",
        "scanned_document.pdf",
        "multi_column_document.pdf",
        "sample.html",
        "sample.md",
        "sample.csv",
        "sample.adoc",
        "sample.png",
        "image.png",
        "sample.docx",
        "sample.pptx",
        "sample.xlsx",
    ],
)
async def test_docling_handles_various_inputs(relative_path: str):
    sample_file = DATA_DIR / relative_path
    extractor = DoclingFileExtractor(_NoopFileService())

    pieces = await extractor.aextract_content(sample_file, sample_file.name)
    assert isinstance(pieces, list)
    for piece in pieces:
        assert piece.page_content is not None


def test_has_meaningful_table_content():
    assert DoclingFileExtractor._has_meaningful_table_content("| A |\n| --- |\n| 1 |") is True
    assert DoclingFileExtractor._has_meaningful_table_content("| --- |\n| --- |") is False


def test_resolve_item_page_prefers_valid_page():
    class _Prov:
        def __init__(self, page_no: int):
            self.page_no = page_no

    class _Item:
        def __init__(self, page_numbers: list[int]):
            self.prov = [_Prov(page) for page in page_numbers]

    assert DoclingFileExtractor._resolve_item_page(_Item([3, 4])) == 3
    assert DoclingFileExtractor._resolve_item_page(_Item([])) == -1


def test_compatible_file_types_cover_all_supported_formats():
    extractor = DoclingFileExtractor.__new__(DoclingFileExtractor)
    expected = {
        docling_module.FileType.PDF,
        docling_module.FileType.DOCX,
        docling_module.FileType.PPTX,
        docling_module.FileType.XLSX,
        docling_module.FileType.HTML,
        docling_module.FileType.MD,
        docling_module.FileType.ASCIIDOC,
        docling_module.FileType.CSV,
        docling_module.FileType.IMAGE,
    }

    assert set(extractor.compatible_file_types) == expected
