from pathlib import Path

import pytest
from PIL import Image

from extractor_api_lib.file_services.file_service import FileService
from extractor_api_lib.impl.extractors.file_extractors.image_extractor import TesseractImageExtractor
from extractor_api_lib.impl.types.content_type import ContentType

import extractor_api_lib.impl.extractors.file_extractors.image_extractor as image_module


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


@pytest.mark.asyncio
async def test_image_extractor_returns_clean_piece(monkeypatch, tmp_path: Path):
    sample_path = tmp_path / "hello.png"
    Image.new("RGB", (50, 50), color="white").save(sample_path)

    extractor = TesseractImageExtractor(_NoopFileService(), languages=["deu", " eng "], psm=7)

    captured: dict[str, str] = {}

    def fake_ocr(frame, lang, config):  # pragma: no cover - simple stub
        captured["lang"] = lang
        captured["config"] = config
        captured["size"] = frame.size
        return " Hello Image "

    monkeypatch.setattr(image_module.pytesseract, "image_to_string", fake_ocr)

    pieces = await extractor.aextract_content(sample_path, sample_path.name)

    assert len(pieces) == 1
    piece = pieces[0]
    assert piece.type == ContentType.TEXT
    assert piece.metadata["origin_extractor"] == "tesseract-image"
    assert piece.metadata["page"] == 1
    assert piece.page_content == "Hello Image"
    assert captured["lang"] == "deu+eng"
    assert captured["config"] == "--psm 7"
    assert captured["size"] == (50, 50)


@pytest.mark.asyncio
async def test_image_extractor_returns_empty_when_ocr_blank(monkeypatch, tmp_path: Path):
    sample_path = tmp_path / "blank.png"
    Image.new("RGB", (20, 20), color="white").save(sample_path)

    extractor = TesseractImageExtractor(_NoopFileService())

    monkeypatch.setattr(image_module.pytesseract, "image_to_string", lambda *_, **__: "   ")

    pieces = await extractor.aextract_content(sample_path, sample_path.name)

    assert pieces == []


@pytest.mark.asyncio
async def test_image_extractor_raises_for_invalid_image(tmp_path: Path):
    invalid_path = tmp_path / "invalid.png"
    invalid_path.write_bytes(b"not an image")

    extractor = TesseractImageExtractor(_NoopFileService())

    with pytest.raises(ValueError):
        await extractor.aextract_content(invalid_path, invalid_path.name)


@pytest.mark.asyncio
async def test_image_extractor_raises_for_multi_frame_image(tmp_path: Path):
    animated_path = tmp_path / "animated.tiff"

    frame_one = Image.new("RGB", (10, 10), color="white")
    frame_two = Image.new("RGB", (10, 10), color="black")
    frame_one.save(animated_path, save_all=True, append_images=[frame_two], format="TIFF")

    extractor = TesseractImageExtractor(_NoopFileService())

    with pytest.raises(ValueError):
        await extractor.aextract_content(animated_path, animated_path.name)
