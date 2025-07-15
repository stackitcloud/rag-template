"""Module for the SitemapLangchainDocument2InformationPiece class."""

from extractor_api_lib.impl.utils.utils import hash_datetime
from extractor_api_lib.mapper.source_langchain_document2information_piece import (
    SourceLangchainDocument2InformationPiece,
)


class SitemapLangchainDocument2InformationPiece(SourceLangchainDocument2InformationPiece):
    """
    A class to map a LangchainDocument to an InformationPiece with Sitemap-specific metadata.

    Attributes
    ----------
    USE_CASE_DOCUMENT_URL_KEY : str
        Key for the document URL in the use case.
    SOURCE_LOADER_SOURCE_URL_KEY : str
        The key for the source URL in the Sitemap loader.
    SOURCE_LOADER_TITLE_KEY : str
        The key for the title in the Sitemap loader.
    USER_CASE_PAGE_KEY : str
        Key for the page in the use case.
    USE_CASE_RELATED_KEY : str
        Key for related information in the use case.
    DOCUMENT_KEY : str
        Key for the document.
    ID_KEY : str
        Key for the unique identifier of the information piece.
    """

    ID_KEY = "id"

    def _map_meta(self, internal: dict, document_name: str) -> dict:
        metadata = {}
        for key, value in internal.items():
            metadata[self.USE_CASE_DOCUMENT_URL_KEY if key == self.SOURCE_LOADER_SOURCE_URL_KEY else key] = value

            page_title_matches = [v for k, v in metadata.items() if k == self.SOURCE_LOADER_TITLE_KEY]
            page_title = page_title_matches[0] if page_title_matches else "Unknown Title"

            metadata[self.USER_CASE_PAGE_KEY] = page_title
            metadata[self.DOCUMENT_KEY] = document_name
            metadata[self.USE_CASE_RELATED_KEY] = []
            metadata[self.ID_KEY] = hash_datetime()
        return metadata
