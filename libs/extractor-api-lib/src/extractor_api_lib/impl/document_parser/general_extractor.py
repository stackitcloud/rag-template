"""Module for the GeneralExtractor class."""

from pathlib import Path
from extractor_api_lib.impl.types.file_type import FileType
from extractor_api_lib.models.dataclasses.information_piece import InformationPiece
from extractor_api_lib.file_services.file_service import FileService
from extractor_api_lib.document_parser.information_extractor import InformationExtractor


class GeneralExtractor(InformationExtractor):
    """A class to extract information from documents using available extractors.

    This class serves as a general extractor that utilizes a list of available
    information extractors to extract content from documents. It determines the
    appropriate extractor based on the file type of the document.
    """

    def __init__(self, file_service: FileService, available_extractors: list[InformationExtractor]):
        """
        Initialize the GeneralExtractor.

        Parameters
        ----------
        file_service : FileService
            An instance of FileService to handle file operations.
        available_extractors : list of InformationExtractor
            A list of available information extractors to be used by the GeneralExtractor.
        """
        super().__init__(file_service=file_service)

        self._available_extractors = available_extractors

    @property
    def compatible_file_types(self) -> list[FileType]:
        """
        List of compatible file types for the document parser.

        Returns
        -------
        list[FileType]
            A list containing the compatible file types. By default, it returns a list with FileType.NONE.
        """
        return [FileType.NONE]

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
        file_type = str(file_path).split(".")[-1].upper()
        correct_extractors = [
            x for x in self._available_extractors if file_type in [y.value for y in x.compatible_file_types]
        ]
        if not correct_extractors:
            raise ValueError(f"No extractor found for file-ending {file_type}")
        return correct_extractors[-1].extract_content(file_path)
