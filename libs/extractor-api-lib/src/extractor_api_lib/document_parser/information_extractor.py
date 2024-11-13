"""Base class for Information extractors."""

from abc import ABC, abstractmethod
from pathlib import Path

from extractor_api_lib.document_parser.file_type import FileType
from extractor_api_lib.document_parser.information_piece import InformationPiece
from extractor_api_lib.file_services.file_service import FileService


class InformationExtractor(ABC):
    """Base class for Information extractors."""

    def __init__(self, file_service: FileService):
        """Base Constructor for InformationExtractor.

        Parameters
        ----------
        file_service : FileService
            Handler for downloading the file to extract content from and upload results to if required.
        """
        self._file_service = file_service

    @property
    @abstractmethod
    def compatible_file_types(self) -> list[FileType]:
        ...

    @abstractmethod
    def extract_content(self, file_path: Path) -> list[InformationPiece]:
        """
        Extract content from given file.

        Parameters
        ----------
        file_path : Path
            Path to the file the information should be extracted from.

        Returns
        -------
        list[InformationPiece]
            The extracted information.
        """
