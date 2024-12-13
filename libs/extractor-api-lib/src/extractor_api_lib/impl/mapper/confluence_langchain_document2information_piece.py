"""Module for the ConfluenceLangchainDocument2InformationPiece class."""

from langchain_core.documents import Document as LangchainDocument

from extractor_api_lib.models.confluence_parameters import ConfluenceParameters
from extractor_api_lib.models.content_type import ContentType
from extractor_api_lib.models.information_piece import InformationPiece
from extractor_api_lib.models.key_value_pair import KeyValuePair as MetaInformationPiece


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

    def __init__(self) -> None:
        """Initialize the ConfluenceLangchainDocument2InformationPiece instance."""
        self._confluence_parameters = None

    @property
    def confluence_parameters(self):
        """
        Property that returns the Confluence parameters.

        Returns
        -------
        dict
            A dictionary containing the Confluence parameters.
        """
        return self._confluence_parameters

    @confluence_parameters.setter
    def confluence_parameters(self, confluence_parameters: ConfluenceParameters):
        """
        Set the confluence parameters.

        Parameters
        ----------
        confluence_parameters : ConfluenceParameters
            The confluence parameters to be set.
        """
        self._confluence_parameters = confluence_parameters

    def map_document2informationpiece(self, document: LangchainDocument) -> InformationPiece:
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
        if self._confluence_parameters is None:
            raise ValueError("Confluence parameters must be set before mapping documents")

        meta = self._map_meta(document.metadata)
        return InformationPiece(page_content=document.page_content, type=ContentType.TEXT, metadata=meta)

    def _map_meta(self, internal: dict) -> list[MetaInformationPiece]:
        metadata = []
        for key, value in internal.items():
            metadata.append(
                MetaInformationPiece(
                    key=self.USE_CASE_DOCUMENT_URL_KEY if key == self.CONFLUENCE_LOADER_SOURCE_URL_KEY else key,
                    value=value,
                )
            )
            page_title_matches = [m.value for m in metadata if m.key == self.CONFLUENCE_LOADER_TITLE_KEY]
            page_title = page_title_matches[0] if page_title_matches else "Unknown Title"

            metadata.append(MetaInformationPiece(key=self.USER_CASE_PAGE_KEY, value=page_title))
            metadata.append(
                MetaInformationPiece(key=self.DOCUMENT_KEY, value=self._confluence_parameters.document_name)
            )
            metadata.append(MetaInformationPiece(key=self.USE_CASE_RELATED_KEY, value=[]))
        return metadata
