"""Module for the ConfluenceLangchainDocument2InformationPiece class."""

from abc import abstractmethod, ABC
from langchain_core.documents import Document as LangchainDocument

from extractor_api_lib.models.dataclasses.internal_information_piece import InternalInformationPiece
from extractor_api_lib.models.content_type import ContentType


class SourceLangchainDocument2InformationPiece(ABC):
    """
    A class to map a LangchainDocument to an InformationPiece with Confluence-specific metadata.

    Attributes
    ----------
    USE_CASE_DOCUMENT_URL_KEY : str
        Key for the document URL in the use case.
    CONFLUENCE_LOADER_SOURCE_URL_KEY : str
        Key for the source URL in the Confluence loader.
    CONFLUENCE_LOADER_TITLE_KEY : str
        Key for the title in the Confluence loader.
    USER_CASE_PAGE_KEY : str
        Key for the page in the use case.
    USE_CASE_RELATED_KEY : str
        Key for related information in the use case.
    DOCUMENT_KEY : str
        Key for the document.
    """

    USE_CASE_DOCUMENT_URL_KEY = "document_url"
    SOURCE_LOADER_SOURCE_URL_KEY = "source"
    SOURCE_LOADER_TITLE_KEY = "title"
    USER_CASE_PAGE_KEY = "page"
    USE_CASE_RELATED_KEY = "related"
    DOCUMENT_KEY = "document"

    def map_document2informationpiece(
        self, document: LangchainDocument, document_name: str
    ) -> InternalInformationPiece:
        """
        Map a LangchainDocument to an InformationPiece.

        Parameters
        ----------
        document : LangchainDocument
            The document to be mapped.

        Returns
        -------
        InformationPiece
            The mapped information piece containing page content, type, and metadata.

        Raises
        ------
        ValueError
            If Confluence parameters are not set before mapping documents.
        """
        meta = self._map_meta(document.metadata, document_name)
        return InternalInformationPiece(page_content=document.page_content, type=ContentType.TEXT, metadata=meta)

    @abstractmethod
    def _map_meta(self, internal: dict, document_name: str) -> dict:
        raise NotImplementedError("Subclasses must implement this method.")
