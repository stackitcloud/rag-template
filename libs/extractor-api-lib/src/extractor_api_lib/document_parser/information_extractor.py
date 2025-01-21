"""Module for the Base class for Information extractors."""

from abc import ABC, abstractmethod
from pathlib import Path

from extractor_api_lib.file_services.file_service import FileService
from extractor_api_lib.impl.types.file_type import FileType
from extractor_api_lib.models.dataclasses.information_piece import InformationPiece


class InformationExtractor(ABC):
    """Base class for Information extractors."""

    def __init__(self, file_service: FileService):
        """Initialize the InformationExtractor.

        Parameters
        ----------
        file_service : FileService
            Handler for downloading the file to extract content from and upload results to if required.
        """
        self._file_service = file_service

    @property
    @abstractmethod
    def compatible_file_types(self) -> list[FileType]:
        """
        Abstract property that should be implemented to return a list of compatible file types.

        Returns
        -------
        list[FileType]
            A list of file types that are compatible with the document parser.
        """

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
