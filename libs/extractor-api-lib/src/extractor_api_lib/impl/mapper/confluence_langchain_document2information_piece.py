"""Module for the ConfluenceLangchainDocument2InformationPiece class."""

from extractor_api_lib.mapper.source_langchain_document2information_piece import (
    SourceLangchainDocument2InformationPiece,
)


class ConfluenceLangchainDocument2InformationPiece(SourceLangchainDocument2InformationPiece):
    """
    A class to map a LangchainDocument to an InformationPiece with Confluence-specific metadata.

    Attributes
    ----------
    USE_CASE_DOCUMENT_URL_KEY : str
        Key for the document URL in the use case.
    SOURCE_LOADER_SOURCE_URL_KEY : str
        Key for the source URL in the Confluence loader.
    SOURCE_LOADER_TITLE_KEY : str
        Key for the title in the Confluence loader.
    USER_CASE_PAGE_KEY : str
        Key for the page in the use case.
    USE_CASE_RELATED_KEY : str
        Key for related information in the use case.
    DOCUMENT_KEY : str
        Key for the document.
    """

    def _map_meta(self, internal: dict, document_name: str) -> dict:
        metadata = {}
        for key, value in internal.items():
            metadata[self.USE_CASE_DOCUMENT_URL_KEY if key == self.SOURCE_LOADER_SOURCE_URL_KEY else key] = value

            page_title_matches = [v for k, v in metadata.items() if k == self.SOURCE_LOADER_TITLE_KEY]
            page_title = page_title_matches[0] if page_title_matches else "Unknown Title"

            metadata[self.USER_CASE_PAGE_KEY] = page_title
            metadata[self.DOCUMENT_KEY] = document_name
            metadata[self.USE_CASE_RELATED_KEY] = []
        return metadata
