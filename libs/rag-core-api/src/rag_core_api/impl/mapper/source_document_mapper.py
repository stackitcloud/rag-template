import json

from langchain_core.documents import Document as LangchainDocument
from rag_core_lib.impl.data_types.content_type import ContentType as InternalContentType

from rag_core_api.models.source_document import SourceDocument
from rag_core_api.models.content_type import ContentType as ExternalContentType
from rag_core_api.models.key_value_pair import KeyValuePair


class SourceDocumentMapper:

    @staticmethod
    def source_document2langchain_document(source_document: SourceDocument) -> LangchainDocument:
        metadata = {x.key: json.loads(x.value) for x in source_document.metadata}
        metadata["type"] = SourceDocumentMapper.external_content2internal_content(metadata["type"]).value
        return LangchainDocument(page_content=source_document.content, metadata=metadata)

    @staticmethod
    def langchain_document2source_document(langchain_document: LangchainDocument) -> SourceDocument:
        metadata = [
            KeyValuePair(key=key, value=json.dumps(value)) for key, value in langchain_document.metadata.items()
        ]
        return SourceDocument(content=langchain_document.page_content, metadata=metadata)

    @staticmethod
    def internal_content2external_content(internal_content_type: str) -> ExternalContentType:
        lookup_table = {
            InternalContentType.IMAGE.value: ExternalContentType.IMAGE,
            InternalContentType.TABLE.value: ExternalContentType.TABLE,
            InternalContentType.SUMMARY.value: ExternalContentType.SUMMARY,
            InternalContentType.TEXT.value: ExternalContentType.TEXT,
        }
        return lookup_table[internal_content_type]

    @staticmethod
    def external_content2internal_content(external_content_type: str) -> InternalContentType:
        lookup_table = {
            ExternalContentType.IMAGE.value: InternalContentType.IMAGE,
            ExternalContentType.TABLE.value: InternalContentType.TABLE,
            ExternalContentType.SUMMARY.value: InternalContentType.SUMMARY,
            ExternalContentType.TEXT.value: InternalContentType.TEXT,
        }
        return lookup_table[external_content_type]
