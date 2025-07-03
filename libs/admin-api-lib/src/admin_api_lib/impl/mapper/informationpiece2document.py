"""Module for mapping between InformationPiece and LangchainDocument."""

import json

from langchain_core.documents import Document as LangchainDocument

from admin_api_lib.extractor_api_client.openapi_client.models.content_type import (
    ContentType as ExtractorInformaType,
)
from admin_api_lib.extractor_api_client.openapi_client.models.information_piece import (
    InformationPiece as ExtractorInformationPiece,
)
from admin_api_lib.rag_backend_client.openapi_client.models.information_piece import (
    InformationPiece as RagInformationPiece,
)
from admin_api_lib.rag_backend_client.openapi_client.models.key_value_pair import (
    KeyValuePair as RagKeyValue,
)
from rag_core_lib.impl.data_types.content_type import ContentType as RagInformationType


class InformationPiece2Document:
    """The InformationPiece2Document class.

    A utility class for converting between ExtractorInformationPiece and LangchainDocument,
    and between LangchainDocument and RagInformationPiece.

    Attributes
    ----------
    LOOKUP_TABLE : dict
        A dictionary mapping ExtractorInformaType to RagInformationType.
    METADATA_TYPE_KEY : str
        The key used to store the type of information piece in metadata.
    """

    LOOKUP_TABLE = {
        ExtractorInformaType.IMAGE: RagInformationType.IMAGE,
        ExtractorInformaType.TABLE: RagInformationType.TABLE,
        ExtractorInformaType.TEXT: RagInformationType.TEXT,
    }
    METADATA_TYPE_KEY = "type"

    @staticmethod
    def extractor_information_piece2document(info: ExtractorInformationPiece) -> LangchainDocument:
        """
        Convert an ExtractorInformationPiece instance to a LangchainDocument instance.

        Parameters
        ----------
        info : ExtractorInformationPiece
            The information piece to be converted, containing metadata page content, type.

        Returns
        -------
        LangchainDocument
            The converted LangchainDocument with the page content, metadata and type.

        Notes
        -----
        The metadata of the resulting LangchainDocument includes all key-value pairs from the
        input metadata, with an additional entry for the type of the information piece.
        """
        metadata = {x.key: x.value for x in info.metadata}
        metadata[InformationPiece2Document.METADATA_TYPE_KEY] = InformationPiece2Document.infotype2infotype(
            info.type
        ).value

        return LangchainDocument(page_content=info.page_content, metadata=metadata)

    @staticmethod
    def document2rag_information_piece(document: LangchainDocument) -> RagInformationPiece:
        """
        Convert a LangchainDocument to a RagInformationPiece.

        Parameters
        ----------
        document : LangchainDocument
            The document to be converted, containing metadata, page content and type.

        Returns
        -------
        RagInformationPiece
            The converted information piece with type, metadata, and page content.
        """
        metadata = [RagKeyValue(key=str(key), value=json.dumps(value)) for key, value in document.metadata.items()]
        content_type = RagInformationType(document.metadata[InformationPiece2Document.METADATA_TYPE_KEY].upper())
        return RagInformationPiece(
            type=content_type,
            metadata=metadata,
            page_content=document.page_content,
        )

    @staticmethod
    def infotype2infotype(info_type: ExtractorInformaType) -> RagInformationType:
        """
        Convert from ExtractorInformaType to RagInformationType.

        Parameters
        ----------
        info_type : ExtractorInformaType
            The external information type to be converted.

        Returns
        -------
        RagInformationType
            The corresponding internal information type.
        """
        return InformationPiece2Document.LOOKUP_TABLE[info_type]
