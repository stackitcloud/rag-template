from fastapi import HTTPException, status

from rag_core.api_endpoints.source_documents_uploader import SourceDocumentsUploader
from rag_core.impl.mapper.upload_source_document2langchain_document import UploadSourceDocument2LangchainDocument
from rag_core.models.upload_source_document import UploadSourceDocument
from rag_core.vector_databases.vector_database import VectorDatabase


class DefaultSourceDocumentsUploader(SourceDocumentsUploader):

    def __init__(self, vector_database: VectorDatabase):
        self._vector_database = vector_database

    def upload_source_documents(self, source_document: list[UploadSourceDocument]):
        langchain_documents = [
            UploadSourceDocument2LangchainDocument.source_document2langchain_document(document)
            for document in source_document
        ]
        try:
            # TODO: maybe put in background task. Just writing to the database should not take so incredibly long
            # (for moderate number of documents). If more users are using the system and upload in parallel,
            # we should think, how to handle that best.
            self._vector_database.upload(langchain_documents)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
