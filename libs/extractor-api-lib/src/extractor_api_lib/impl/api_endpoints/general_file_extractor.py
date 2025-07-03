"""Module for the GeneralExtractor class."""

import logging
from pathlib import Path
import tempfile
import traceback


from extractor_api_lib.api_endpoints.file_extractor import FileExtractor
from extractor_api_lib.impl.mapper.internal2external_information_piece import Internal2ExternalInformationPiece
from extractor_api_lib.models.extraction_request import ExtractionRequest
from extractor_api_lib.file_services.file_service import FileService
from extractor_api_lib.extractors.information_file_extractor import InformationFileExtractor
from extractor_api_lib.models.information_piece import InformationPiece

logger = logging.getLogger(__name__)


class GeneralFileExtractor(FileExtractor):
    """A class to extract information from documents using available extractors.

    This class serves as a general extractor that utilizes a list of available
    information extractors to extract content from documents. It determines the
    appropriate extractor based on the file type of the document.
    """

    def __init__(
        self,
        file_service: FileService,
        available_extractors: list[InformationFileExtractor],
        mapper: Internal2ExternalInformationPiece,
    ):
        """
        Initialize the GeneralExtractor.

        Parameters
        ----------
        file_service : FileService
            An instance of FileService to handle file operations.
        available_extractors : list of InformationExtractor
            A list of available information extractors to be used by the GeneralExtractor.
        """
        self._file_service = file_service
        self._available_extractors = available_extractors
        self._mapper = mapper

    async def aextract_information(self, extraction_request: ExtractionRequest) -> list[InformationPiece]:
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
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_file_path = Path(temp_dir) / Path(extraction_request.path_on_s3).name
                with open(temp_file_path, "wb") as temp_file:
                    self._file_service.download_file(extraction_request.path_on_s3, temp_file)
                    logger.debug("Temporary file created at %s.", temp_file_path)
                    logger.debug("Temp file created and content written.")
                file_type = str(temp_file_path).split(".")[-1].upper()
                correct_extractors = [
                    x for x in self._available_extractors if file_type in [y.value for y in x.compatible_file_types]
                ]
                if not correct_extractors:
                    raise ValueError(f"No extractor found for file-ending {file_type}")
                results = await correct_extractors[-1].aextract_content(
                    temp_file_path, extraction_request.document_name
                )
                return [self._mapper.map_internal_to_external(x) for x in results if x.page_content is not None]
        except Exception as e:
            logger.error("Error during document parsing: %s %s", e, traceback.format_exc())
            raise e
