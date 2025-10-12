"""Module containing the MarkdownExtractor class."""

from pathlib import Path
from typing import Any, Optional


from extractor_api_lib.file_services.file_service import FileService
from extractor_api_lib.extractors.information_file_extractor import InformationFileExtractor
from extractor_api_lib.impl.types.content_type import ContentType
from extractor_api_lib.impl.types.file_type import FileType
from extractor_api_lib.impl.utils.utils import hash_datetime, sanitize_file_name
from extractor_api_lib.models.dataclasses.internal_information_piece import InternalInformationPiece


class MarkdownExtractor(InformationFileExtractor):
    """Simple extractor for Markdown (.md) files.

    The extractor reads the markdown file content and returns a single
    text information piece containing the markdown source. This keeps
    markdown formatting for downstream rendering.
    """

    def __init__(self, file_service: FileService):
        super().__init__(file_service=file_service)

    @property
    def compatible_file_types(self) -> list[FileType]:
        return [FileType.MD]

    async def aextract_content(self, file_path: Path, name: str) -> list[InternalInformationPiece]:
        # Simply read the file from disk (it has already been downloaded by the general extractor)
        text = ""
        try:
            text = file_path.read_text(encoding="utf-8")
        except Exception:
            # fallback to binary read and decode
            text = file_path.read_bytes().decode(errors="ignore")

        return [
            self._create_information_piece(document_name=name, content=text, content_type=ContentType.TEXT)
        ]

    def _create_information_piece(
        self,
        document_name: str,
        content: str,
        content_type: ContentType,
        additional_meta: Optional[dict[str, Any]] = None,
    ) -> InternalInformationPiece:
        metadata = {
            "document": document_name,
            "file_name": sanitize_file_name(document_name, strip_extension=True),
            "id": hash_datetime(),
            "related": [],
        }
        if additional_meta:
            metadata.update(additional_meta)
        return InternalInformationPiece(type=content_type, metadata=metadata, page_content=content)
