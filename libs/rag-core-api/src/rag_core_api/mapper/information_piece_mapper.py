"""Module for mapping between LangchainDocument and InformationPiece."""

import json

from langchain_core.documents import Document as LangchainDocument

from rag_core_api.models.content_type import ContentType as ExternalContentType
from rag_core_api.models.information_piece import InformationPiece
from rag_core_api.models.key_value_pair import KeyValuePair
from rag_core_lib.impl.data_types.content_type import ContentType as InternalContentType


class InformationPieceMapper:
    """
    A mapper class for converting between LangchainDocument and InformationPiece.

    This class provides static methods to handle bidirectional conversion between
    LangchainDocument and InformationPiece objects, as well as content type conversions.

    Attributes
    ----------
    DOCUMENT_URL_KEY : str
        Key for document URL in metadata
    IMAGE_CONTENT_KEY : str
        Key for base64 image content in metadata
    """

    DOCUMENT_URL_KEY = "document_url"
    IMAGE_CONTENT_KEY = "base64_image"

    @staticmethod
    def information_piece2langchain_document(
        information_piece: InformationPiece,
    ) -> LangchainDocument:
        """
        Convert an InformationPiece instance to a LangchainDocument instance.

        Parameters
        ----------
        information_piece : InformationPiece
            The information piece to be converted.

        Returns
        -------
        LangchainDocument
            The converted LangchainDocument instance.

        Raises
        ------
        ValueError
            If the required key `DOCUMENT_URL_KEY` is not found in the metadata.
            If the required key for content-type `IMAGE` is not found in the metadata when the type is `IMAGE`.
        """
        metadata = {x.key: json.loads(x.value) for x in information_piece.metadata}
        if InformationPieceMapper.DOCUMENT_URL_KEY not in metadata.keys():
            raise ValueError('Required key "%s" not found in metadata.' % InformationPieceMapper.DOCUMENT_URL_KEY)
        metadata["type"] = InformationPieceMapper.external_content2internal_content(metadata["type"]).value
        if (
            metadata["type"] == InternalContentType.IMAGE
            and InformationPieceMapper.IMAGE_CONTENT_KEY not in metadata.keys()
        ):
            raise ValueError(
                'Required key "%s" for content-type %s not found in metadata.'
                % (InternalContentType.IMAGE, InformationPieceMapper.IMAGE_CONTENT_KEY)
            )
        return LangchainDocument(page_content=information_piece.page_content, metadata=metadata)

    @staticmethod
    def langchain_document2information_piece(
        langchain_document: LangchainDocument,
    ) -> InformationPiece:
        """
        Convert a LangchainDocument to an InformationPiece.

        Parameters
        ----------
        langchain_document : LangchainDocument
            The LangchainDocument instance to be converted.

        Returns
        -------
        InformationPiece
            The converted InformationPiece instance, with metadata converted to key-value pairs
            and type set to the value from metadata or ExternalContentType.TEXT.value (default).
        """
        metadata = InformationPieceMapper._dict2key_value_pair(langchain_document.metadata)
        return InformationPiece(
            page_content=langchain_document.page_content,
            metadata=metadata,
            type=langchain_document.metadata.get("type", ExternalContentType.TEXT.value),
        )

    @staticmethod
    def internal_content2external_content(
        internal_content_type: str,
    ) -> ExternalContentType:
        """
        Convert an internal content type to an external content type.

        Parameters
        ----------
        internal_content_type : str
            The internal content type to be converted.

        Returns
        -------
        ExternalContentType
            The corresponding external content type.

        Raises
        ------
        KeyError
            If the internal content type is not found in the lookup table.
        """
        lookup_table = {
            InternalContentType.IMAGE.value: ExternalContentType.IMAGE,
            InternalContentType.TABLE.value: ExternalContentType.TABLE,
            InternalContentType.SUMMARY.value: ExternalContentType.SUMMARY,
            InternalContentType.TEXT.value: ExternalContentType.TEXT,
        }
        return lookup_table[internal_content_type]

    @staticmethod
    def external_content2internal_content(
        external_content_type: str,
    ) -> InternalContentType:
        """
        Convert external content type to internal content type.

        Parameters
        ----------
        external_content_type : str
            The external content type as a string.

        Returns
        -------
        InternalContentType
            The corresponding internal content type.

        Raises
        ------
        KeyError
            If the external content type is not found in the lookup table.
        """
        lookup_table = {
            ExternalContentType.IMAGE.value: InternalContentType.IMAGE,
            ExternalContentType.TABLE.value: InternalContentType.TABLE,
            ExternalContentType.SUMMARY.value: InternalContentType.SUMMARY,
            ExternalContentType.TEXT.value: InternalContentType.TEXT,
        }
        return lookup_table[external_content_type]

    @staticmethod
    def _dict2key_value_pair(metadata: dict[str, any]) -> list[KeyValuePair]:
        mapped_values = []
        for key, value in metadata.items():
            mapped_item: KeyValuePair | None = None

            match value:
                case dict():
                    mapped_item = KeyValuePair(key=key, value=json.dumps(value))
                case _:
                    mapped_item = KeyValuePair(key=key, value=json.dumps(str(value)))

            mapped_values.append(mapped_item)
        return mapped_values
