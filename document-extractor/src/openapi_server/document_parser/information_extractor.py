"""Base class for Information extractors."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from openapi_server.document_parser.file_type import FileType
from openapi_server.file_services.file_service import FileService
from openapi_server.models.information_piece import InformationPiece


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
    def compatible_file_types(self) -> List[FileType]: ...

    @abstractmethod
    def extract_content(self, file_path: Path) -> List[InformationPiece]:
        """
        Extract content from given file.

        Parameters
        ----------
        file_path : Path
            Path to the file the information should be extracted from.

        Returns
        -------
        List[InformationPiece]
            The extracted information.
        """
