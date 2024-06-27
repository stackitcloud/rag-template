import json

from langchain_core.documents import Document as LangchainDocument

from rag_core.models.upload_source_document import UploadSourceDocument
from rag_core.models.content_type import ContentType as ExternalContentType
from rag_core.impl.data_types.content_type import ContentType as InternalContentType


class UploadSourceDocument2LangchainDocument:
    LOOKUP_TABLE = {
        ExternalContentType.IMAGE: InternalContentType.IMAGE,
        ExternalContentType.TABLE: InternalContentType.TABLE,
        ExternalContentType.SUMMARY: InternalContentType.SUMMARY,
        ExternalContentType.TEXT: InternalContentType.TEXT,
    }

    @staticmethod
    def source_document2langchain_document(source_document: UploadSourceDocument) -> LangchainDocument:
        metadata = {x.key: json.loads(x.value) for x in source_document.metadata}
        metadata["type"] = UploadSourceDocument2LangchainDocument.LOOKUP_TABLE[source_document.content_type.name].value
        return LangchainDocument(page_content=source_document.content, metadata=metadata)
