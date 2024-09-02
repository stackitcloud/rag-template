from langchain_core.documents import Document as LangchainDocument
from rag_core_lib.impl.data_types.content_type import ContentType as InternalInformationType

from admin_backend.document_extractor_client.openapi_client.models.information_type import (
    InformationType as ExternalInformaType,
)
from admin_backend.document_extractor_client.openapi_client.models.information_piece import InformationPiece


class InformationPiece2Document:
    LOOKUP_TABLE = {
        ExternalInformaType.IMAGE: InternalInformationType.IMAGE,
        ExternalInformaType.TABLE: InternalInformationType.TABLE,
        ExternalInformaType.TEXT: InternalInformationType.TEXT,
    }
    METADATA_TYPE_KEY = "type"

    @staticmethod
    def information_piece2document(info: InformationPiece) -> LangchainDocument:
        metadata = {x.key: x.value for x in info.meta_information}
        metadata[InformationPiece2Document.METADATA_TYPE_KEY] = InformationPiece2Document.infotype2infotype(
            info.type.name
        ).value

        return LangchainDocument(page_content=info.content, metadata=metadata)

    @staticmethod
    def infotype2infotype(
        info_type: ExternalInformaType,
    ) -> InternalInformationType:
        return InformationPiece2Document.LOOKUP_TABLE[info_type]
