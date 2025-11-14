from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, Sequence

from PIL import Image, ImageSequence, UnidentifiedImageError
import pytesseract
from pytesseract import TesseractError

from extractor_api_lib.extractors.information_file_extractor import InformationFileExtractor
from extractor_api_lib.file_services.file_service import FileService
from extractor_api_lib.impl.types.content_type import ContentType
from extractor_api_lib.impl.types.file_type import FileType
from extractor_api_lib.impl.utils.utils import hash_datetime
from extractor_api_lib.models.dataclasses.internal_information_piece import InternalInformationPiece

# Assumptions:
# - Tesseract CLI is present in the runtime image for pytesseract to shell out to.
# - Image files are already downloaded to local storage via the FileService before extraction runs.

logger = logging.getLogger(__name__)


class TesseractImageExtractor(InformationFileExtractor):
    """InformationFileExtractor specialization that OCRs image files via Tesseract."""

    DEFAULT_LANGUAGES: tuple[str, ...] = ("eng","deu")
    ORIGIN = "tesseract-image"

    def __init__(self, file_service: FileService, languages: Sequence[str] | None = None, psm: int = 6):
        super().__init__(file_service)
        self._languages = self._sanitize_languages(languages)
        self._tesseract_config = f"--psm {psm}"

    @property
    def compatible_file_types(self) -> list[FileType]:
        return [FileType.IMAGE]

    async def aextract_content(self, file_path: Path, name: str) -> list[InternalInformationPiece]:
        try:
            with Image.open(file_path) as image:
                frames = list(self._enumerate_frames(image))
        except UnidentifiedImageError as exc:
            raise ValueError(f"Unsupported image file: {file_path}") from exc

        pieces: list[InternalInformationPiece] = []
        for page, frame in frames:
            text = self._perform_ocr(frame)
            if not text:
                continue
            pieces.append(self._build_piece(document_name=name, page=page, content=text))

        if not pieces:
            logger.info("No OCR content produced for image file: %s", file_path)

        return pieces

    def _perform_ocr(self, frame: Image.Image) -> str:
        try:
            text = pytesseract.image_to_string(frame, lang=self._ocr_language, config=self._tesseract_config)
        except TesseractError as exc:  # pragma: no cover - defensive logging
            logger.warning("Tesseract OCR failed: %s", exc)
            return ""

        return text.strip()

    def _enumerate_frames(self, image: Image.Image) -> Iterable[tuple[int, Image.Image]]:
        produced = False
        for index, frame in enumerate(ImageSequence.Iterator(image), start=1):
            produced = True
            yield index, frame.convert("RGB")

        if not produced:
            yield 1, image.convert("RGB")

    @property
    def _ocr_language(self) -> str:
        return "+".join(self._languages)

    def _sanitize_languages(self, languages: Sequence[str] | None) -> list[str]:
        normalized = [lang.strip() for lang in languages or self.DEFAULT_LANGUAGES if lang and lang.strip()]
        return normalized or list(self.DEFAULT_LANGUAGES)

    def _build_piece(self, document_name: str, page: int, content: str) -> InternalInformationPiece:
        metadata = {
            "document": document_name,
            "page": page,
            "id": hash_datetime(),
            "related": [],
            "origin_extractor": self.ORIGIN,
            "format": "markdown",
        }
        return InternalInformationPiece(type=ContentType.TEXT, metadata=metadata, page_content=content)
