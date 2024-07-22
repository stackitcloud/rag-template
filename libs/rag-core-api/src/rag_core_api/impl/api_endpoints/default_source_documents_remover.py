import logging
import json

from fastapi import HTTPException, status

from rag_core_api.models.delete_request import DeleteRequest

from rag_core_api.api_endpoints.source_documents_remover import SourceDocumentsRemover
from rag_core_api.vector_databases.vector_database import VectorDatabase


logger = logging.getLogger(__name__)


class DefaultSourceDocumentsRemover(SourceDocumentsRemover):

    def __init__(self, vector_database: VectorDatabase):
        self._vector_database = vector_database

    def remove_source_documents(self, delete_request: DeleteRequest) -> None:
        logger.info("Deleting documents from vector database")
        try:
            metadata = {}
            for key_value_pair in delete_request.metadata:
                metadata["metadata." + key_value_pair.key] = json.loads(key_value_pair.value)
        except Exception as e:
            logger.error("Error while parsing metadata: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error while parsing metadata: %s" % e,
            )
        if not metadata:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No search parameters found.",
            )
        try:
            self._vector_database.delete(metadata)
        except Exception as e:
            logger.error("Error while deleting from vector db: %s", e)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Error while deleting %s from vector db" % delete_request.metadata,
            )
