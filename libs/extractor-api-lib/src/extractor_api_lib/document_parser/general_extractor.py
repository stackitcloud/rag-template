from pathlib import Path
from extractor_api_lib.document_parser.file_type import FileType
from extractor_api_lib.document_parser.information_piece import InformationPiece
from extractor_api_lib.file_services.file_service import FileService
from extractor_api_lib.document_parser.information_extractor import InformationExtractor


class GeneralExtractor(InformationExtractor):
    def __init__(self, file_service: FileService, available_extractors: list[InformationExtractor]):
        super().__init__(file_service=file_service)

        self._available_extractors = available_extractors

    @property
    def compatible_file_types(self) -> list[FileType]:
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
