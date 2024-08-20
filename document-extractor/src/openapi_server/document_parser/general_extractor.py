from pathlib import Path
from typing import List
from openapi_server.document_parser.file_type import FileType
from openapi_server.document_parser.information_piece import InformationPiece
from openapi_server.file_services.file_service import FileService
from openapi_server.document_parser.information_extractor import InformationExtractor


class GeneralExtractor(InformationExtractor):
    def __init__(self, file_service: FileService, available_extractors: List[InformationExtractor]):
        super().__init__(file_service=file_service)

        self._available_extractors = available_extractors

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
        file_type = str(file_path).split(".")[-1].upper()
        correct_extractors = [
            x for x in self._available_extractors if file_type in [y.value for y in x.compatible_file_types]
        ]
        assert len(correct_extractors) > 0, "No extractor found for file-ending %s" % file_type
        return correct_extractors[-1].extract_content(file_path)

    @property
    def compatible_file_types(self) -> List[FileType]:
        return [FileType.NONE]
