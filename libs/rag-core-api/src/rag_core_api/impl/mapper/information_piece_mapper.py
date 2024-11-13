import json

from langchain_core.documents import Document as LangchainDocument
from rag_core_lib.impl.data_types.content_type import ContentType as InternalContentType

from rag_core_api.models.information_piece import InformationPiece
from rag_core_api.models.content_type import ContentType as ExternalContentType
from rag_core_api.models.key_value_pair import KeyValuePair


class InformationPieceMapper:
    DOCUMENT_URL_KEY = "document_url"
    IMAGE_CONTENT_KEY = "base64_image"

    @staticmethod
    def information_piece2langchain_document(
        information_piece: InformationPiece,
    ) -> LangchainDocument:
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
            mapped_item: KeyValuePair = ...

            match value:
                case dict():
                    mapped_item = KeyValuePair(key=key, value=json.dumps(value))
                case _:
                    mapped_item = KeyValuePair(key=key, value=json.dumps(str(value)))

            mapped_values.append(mapped_item)
        return mapped_values
