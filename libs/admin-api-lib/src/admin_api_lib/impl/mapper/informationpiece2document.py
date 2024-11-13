from langchain_core.documents import Document as LangchainDocument
from rag_core_lib.impl.data_types.content_type import ContentType as InternalInformationType

from admin_api_lib.extractor_api_client.openapi_client.models.content_type import (
    ContentType as ExternalInformaType,
)
from admin_api_lib.extractor_api_client.openapi_client.models.information_piece import InformationPiece


class InformationPiece2Document:
    LOOKUP_TABLE = {
        ExternalInformaType.IMAGE: InternalInformationType.IMAGE,
        ExternalInformaType.TABLE: InternalInformationType.TABLE,
        ExternalInformaType.TEXT: InternalInformationType.TEXT,
    }
    METADATA_TYPE_KEY = "type"

    @staticmethod
    def information_piece2document(info: InformationPiece) -> LangchainDocument:
        metadata = {x.key: x.value for x in info.metadata}
        metadata[InformationPiece2Document.METADATA_TYPE_KEY] = InformationPiece2Document.infotype2infotype(
            info.type
        ).value

        return LangchainDocument(page_content=info.page_content, metadata=metadata)

    @staticmethod
    def infotype2infotype(
        info_type: ExternalInformaType,
    ) -> InternalInformationType:
        return InformationPiece2Document.LOOKUP_TABLE[info_type]
