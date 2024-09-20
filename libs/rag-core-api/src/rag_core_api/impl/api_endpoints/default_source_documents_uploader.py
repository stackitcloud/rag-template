from fastapi import HTTPException, status

from rag_core_api.impl.mapper.source_document_mapper import SourceDocumentMapper
from rag_core_api.models.upload_source_document import UploadSourceDocument

from rag_core_api.api_endpoints.source_documents_uploader import SourceDocumentsUploader
from rag_core_api.vector_databases.vector_database import VectorDatabase


class DefaultSourceDocumentsUploader(SourceDocumentsUploader):

    def __init__(self, vector_database: VectorDatabase):
        self._vector_database = vector_database

    def upload_source_documents(self, source_document: list[UploadSourceDocument]):
        langchain_documents = [
            SourceDocumentMapper.source_document2langchain_document(document) for document in source_document
        ]
        try:
            self._vector_database.upload(langchain_documents)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
