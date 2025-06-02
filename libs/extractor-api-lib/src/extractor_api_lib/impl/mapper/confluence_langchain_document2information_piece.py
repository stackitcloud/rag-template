"""Module for the ConfluenceLangchainDocument2InformationPiece class."""

from langchain_core.documents import Document as LangchainDocument

from extractor_api_lib.models.dataclasses.internal_information_piece import InternalInformationPiece
from extractor_api_lib.models.content_type import ContentType


class ConfluenceLangchainDocument2InformationPiece:
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
    CONFLUENCE_LOADER_SOURCE_URL_KEY = "source"
    CONFLUENCE_LOADER_TITLE_KEY = "title"
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

    def _map_meta(self, internal: dict, document_name: str) -> dict:
        metadata = {}
        for key, value in internal.items():
            metadata[self.USE_CASE_DOCUMENT_URL_KEY if key == self.CONFLUENCE_LOADER_SOURCE_URL_KEY else key] = value

            page_title_matches = [v for k, v in metadata.items() if k == self.CONFLUENCE_LOADER_TITLE_KEY]
            page_title = page_title_matches[0] if page_title_matches else "Unknown Title"

            metadata[self.USER_CASE_PAGE_KEY] = page_title
            metadata[self.DOCUMENT_KEY] = document_name
            metadata[self.USE_CASE_RELATED_KEY] = []
        return metadata
