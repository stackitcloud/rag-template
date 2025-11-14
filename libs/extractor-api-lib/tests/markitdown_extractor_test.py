from pathlib import Path

import pytest

from extractor_api_lib.file_services.file_service import FileService
from extractor_api_lib.impl.extractors.file_extractors.markitdown_extractor import MarkitdownFileExtractor
from extractor_api_lib.impl.types.content_type import ContentType


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


class _StubResult:
    def __init__(self, **attrs):
        for key, value in attrs.items():
            setattr(self, key, value)


class _StubConverter:
    def __init__(self, result: object):
        self._result = result
        self.calls: list[str] = []

    def convert_stream(self, _stream, filename: str):
        self.calls.append(filename)
        return self._result


DATA_DIR = Path(__file__).parent / "test_data"


@pytest.fixture()
def markitdown_extractor() -> MarkitdownFileExtractor:
    return MarkitdownFileExtractor(_NoopFileService())


@pytest.mark.parametrize(
    "result, expected",
    [
        (_StubResult(markdown="primary", text_content="secondary"), "primary"),
        (_StubResult(text_content=" fallback "), " fallback "),
        (_StubResult(text="legacy"), "legacy"),
        ("raw", "raw"),
        (None, ""),
    ],
)
def test_extract_markdown_prefers_available_fields(result, expected):
    assert MarkitdownFileExtractor._extract_markdown(result) == expected


def test_extract_markdown_tables_detects_all_tables(markitdown_extractor: MarkitdownFileExtractor):
    markdown = """
Intro paragraph

| A | B |
| --- | --- |
| 1 | 2 |

Intermezzo

| C | D |
| --- | --- |
| 3 | 4 |
""".strip()

    tables = markitdown_extractor._extract_markdown_tables(markdown)

    assert len(tables) == 2
    assert tables[0].startswith("| A | B |")
    assert "| 3 | 4 |" in tables[1]


def test_build_pieces_for_markdown_emits_table_metadata(markitdown_extractor: MarkitdownFileExtractor):
    markdown = """# Heading

| Name | Value |
| ---- | ----- |
| Foo | Bar |
"""

    pieces = list(markitdown_extractor._build_pieces_for_markdown("doc", page=7, markdown=markdown))

    assert len(pieces) == 2
    text_piece = pieces[0]
    assert text_piece.type == ContentType.TEXT
    assert text_piece.metadata["origin_extractor"] == "markitdown"
    assert text_piece.metadata["page"] == 7

    table_piece = pieces[1]
    assert table_piece.type == ContentType.TABLE
    assert table_piece.metadata["table_index"] == 1
    assert "| Name | Value |" in table_piece.page_content


def test_split_pptx_markdown_uses_markers(markitdown_extractor: MarkitdownFileExtractor):
    markdown = """
Intro
<!-- Slide number: 1 -->
Slide one body
<!-- Slide number: 3 -->
Slide three body
""".strip()

    slides = markitdown_extractor._split_pptx_markdown(markdown)

    assert slides == [
        (1, "<!-- Slide number: 1 -->\nSlide one body"),
        (3, "<!-- Slide number: 3 -->\nSlide three body"),
    ]


def test_split_pptx_markdown_without_markers_defaults_to_single_chunk(markitdown_extractor: MarkitdownFileExtractor):
    slides = markitdown_extractor._split_pptx_markdown("Single chunk content")

    assert slides == [(1, "Single chunk content")]


@pytest.mark.asyncio
async def test_aextract_content_routes_pdf_through_page_extractor(
    tmp_path: Path, markitdown_extractor: MarkitdownFileExtractor
):
    pdf_path = tmp_path / "report.pdf"
    pdf_path.write_bytes(b"%PDF-FAKE")

    expected = [object()]

    def fake_extract(file_path: Path, document_name: str):
        assert file_path == pdf_path
        assert document_name == pdf_path.name
        return expected

    markitdown_extractor._extract_pdf_pages = fake_extract  # type: ignore[method-assign]

    pieces = await markitdown_extractor.aextract_content(pdf_path, pdf_path.name)

    assert pieces is expected


@pytest.mark.asyncio
async def test_aextract_content_pptx_splits_per_slide(tmp_path: Path, markitdown_extractor: MarkitdownFileExtractor):
    pptx_path = tmp_path / "deck.pptx"
    pptx_path.write_bytes(b"fake pptx")

    markdown = """<!-- Slide number: 1 -->\nSlide 1 body\n<!-- Slide number: 2 -->\nSlide 2 body"""
    stub = _StubConverter(_StubResult(markdown=markdown))
    markitdown_extractor._converter = stub

    pieces = await markitdown_extractor.aextract_content(pptx_path, pptx_path.name)

    assert stub.calls == [pptx_path.name]
    slide_pages = [piece.metadata["page"] for piece in pieces if piece.type == ContentType.TEXT]
    assert slide_pages == [1, 2]


@pytest.mark.asyncio
async def test_aextract_content_returns_single_page_for_text(tmp_path: Path, markitdown_extractor: MarkitdownFileExtractor):
    txt_path = tmp_path / "notes.txt"
    txt_path.write_text("Hello world")

    markdown = "# Title\n\nBody"
    markitdown_extractor._converter = _StubConverter(_StubResult(markdown=markdown))

    pieces = await markitdown_extractor.aextract_content(txt_path, txt_path.name)

    assert len(pieces) == 1
    text_piece = pieces[0]
    assert text_piece.type == ContentType.TEXT
    assert text_piece.metadata["page"] == 1
    assert "Title" in text_piece.page_content


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "relative_path",
    [
        "mixed_content_document.pdf",
        "multi_column_document.pdf",
        "scanned_document.pdf",
        "text_based_document.pdf",
        "sample.html",
        "plain.txt",
        "sample.csv",
        "sample.txt",
        "LoremIpsum.epub",
    ],
)
async def test_markitdown_handles_various_inputs(relative_path: str):
    sample_file = DATA_DIR / relative_path
    extractor = MarkitdownFileExtractor(_NoopFileService())

    # For integration tests: ensure extractor runs without raising and returns 0..n pieces
    pieces = await extractor.aextract_content(sample_file, sample_file.name)
    assert isinstance(pieces, list) and pieces or relative_path == "scanned_document.pdf" and not pieces
    # If we got any pieces, ensure their metadata mentions origin when expected
    for piece in pieces:
        assert piece.page_content is not None
        if piece.type == ContentType.TABLE:
            assert piece.metadata.get("origin_extractor") in ("markitdown", None)
