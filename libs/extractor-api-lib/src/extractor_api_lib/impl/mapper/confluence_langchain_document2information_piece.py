from langchain_core.documents import Document as LangchainDocument

from extractor_api_lib.models.key_value_pair import KeyValuePair as MetaInformationPiece
from extractor_api_lib.models.confluence_parameters import ConfluenceParameters
from extractor_api_lib.models.information_piece import InformationPiece
from extractor_api_lib.models.content_type import ContentType


class ConfluenceLangchainDocument2InformationPiece:
    USE_CASE_DOCUMENT_URL_KEY = "document_url"
    CONFLUENCE_LOADER_SOURCE_URL_KEY = "source"
    CONFLUENCE_LOADER_TITLE_KEY = "title"
    USER_CASE_PAGE_KEY = "page"
    USE_CASE_RELATED_KEY = "related"
    DOCUMENT_KEY = "document"

    def __init__(self) -> None:
        self._confluence_parameters = None

    @property
    def confluence_parameters(self):
        return self._confluence_parameters

    @confluence_parameters.setter
    def confluence_parameters(self, confluence_parameters: ConfluenceParameters):
        self._confluence_parameters = confluence_parameters

    def map_document2informationpiece(self, document: LangchainDocument) -> InformationPiece:
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
            metadata.append(MetaInformationPiece(key=self.DOCUMENT_KEY, value=self._confluence_parameters.url))
            metadata.append(MetaInformationPiece(key=self.USE_CASE_RELATED_KEY, value=[]))
        return metadata
