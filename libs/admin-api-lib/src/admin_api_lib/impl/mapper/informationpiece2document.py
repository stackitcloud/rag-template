from langchain_core.documents import Document as LangchainDocument
from rag_core_lib.impl.data_types.content_type import ContentType as RagInformationType
from admin_api_lib.extractor_api_client.openapi_client.models.content_type import ContentType as ExtractorInformaType
from admin_api_lib.extractor_api_client.openapi_client.models.information_piece import (
    InformationPiece as ExtractorInformationPiece,
)
from admin_api_lib.rag_backend_client.openapi_client.models.key_value_pair import KeyValuePair as RagKeyValue
from admin_api_lib.rag_backend_client.openapi_client.models.information_piece import (
    InformationPiece as RagInformationPiece,
)

import json


class InformationPiece2Document:
    LOOKUP_TABLE = {
        ExtractorInformaType.IMAGE: RagInformationType.IMAGE,
        ExtractorInformaType.TABLE: RagInformationType.TABLE,
        ExtractorInformaType.TEXT: RagInformationType.TEXT,
    }
    METADATA_TYPE_KEY = "type"

    @staticmethod
    def extractor_information_piece2document(info: ExtractorInformationPiece) -> LangchainDocument:
        """Convert from InformationPiece to LangchainDocument"""
        metadata = {x.key: x.value for x in info.metadata}
        metadata[InformationPiece2Document.METADATA_TYPE_KEY] = InformationPiece2Document.infotype2infotype(
            info.type
        ).value

        return LangchainDocument(page_content=info.page_content, metadata=metadata)

    @staticmethod
    def document2rag_information_piece(document: LangchainDocument) -> RagInformationPiece:
        """Convert from LangchainDocument to InformationPiece"""
        metadata = [RagKeyValue(key=str(key), value=json.dumps(value)) for key, value in document.metadata.items()]
        content_type = RagInformationType(document.metadata[InformationPiece2Document.METADATA_TYPE_KEY].upper())
        return RagInformationPiece(
            type=content_type,
            metadata=metadata,
            page_content=document.page_content,
        )

    @staticmethod
    def infotype2infotype(info_type: ExtractorInformaType) -> RagInformationType:
        """Convert from external to internal information type"""
        return InformationPiece2Document.LOOKUP_TABLE[info_type]
