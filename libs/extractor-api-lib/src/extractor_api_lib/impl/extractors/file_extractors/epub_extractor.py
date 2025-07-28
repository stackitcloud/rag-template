"""Module containing the EpubExtractor class."""

import logging
from pathlib import Path

from langchain_community.document_loaders import UnstructuredEPubLoader

from extractor_api_lib.extractors.information_file_extractor import (
    InformationFileExtractor,
)
from extractor_api_lib.file_services.file_service import FileService
from extractor_api_lib.impl.mapper.langchain_document2information_piece import (
    LangchainDocument2InformationPiece,
)
from extractor_api_lib.impl.types.file_type import FileType
from extractor_api_lib.models.dataclasses.internal_information_piece import (
    InternalInformationPiece,
)

logger = logging.getLogger(__name__)


class EpubExtractor(InformationFileExtractor):
    """Extractor for Epub documents using unstructured library."""

    def __init__(
        self,
        file_service: FileService,
        mapper: LangchainDocument2InformationPiece,
    ):
        """Initialize the EpubExtractor.

        Parameters
        ----------
        file_service : FileService
            Handler for downloading the file to extract content from and upload results to if required.
        mapper : LangchainDocument2InformationPiece
            An instance of LangchainDocument2InformationPiece used for mapping langchain documents
            to information pieces.
        """
        super().__init__(file_service=file_service)
        self._mapper = mapper

    @property
    def compatible_file_types(self) -> list[FileType]:
        """
        List of compatible file types for the EPUB extractor.

        Returns
        -------
        list[FileType]
            A list containing the compatible file types, which in this case is EPUB.
        """
        return [FileType.EPUB]

    async def aextract_content(self, file_path: Path, name: str) -> list[InternalInformationPiece]:
        """
        Extract content from an epub file and processes the elements.

        Parameters
        ----------
        file_path : Path
            The path to the epub file to be processed.
        name : str
            Name of the document.

        Returns
        -------
        list[InformationPiece]
            A list of processed information pieces extracted from the epub file.
        """
        elements = UnstructuredEPubLoader(file_path.as_posix()).load()
        return [self._mapper.map_document2informationpiece(document=x, document_name=name) for x in elements]
