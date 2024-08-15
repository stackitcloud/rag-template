import logging

from fastapi import HTTPException, status
from langchain_core.runnables import RunnableConfig

from rag_core_api.impl.mapper.source_document_mapper import SourceDocumentMapper
from rag_core_api.models.chat_response import ChatResponse
from rag_core_api.models.content_type import ContentType
from rag_core_api.models.search_request import SearchRequest
from rag_core_api.models.search_response import SearchResponse
from rag_core_api.models.source_documents import SourceDocuments
from rag_core_api.api_endpoints.searcher import Searcher
from rag_core_api.retriever.retriever import Retriever
from rag_core_api.impl.retriever.no_or_empty_collection_error import NoOrEmptyCollectionError
from rag_core_api.impl.settings.error_messages import ErrorMessages


logger = logging.getLogger(__name__)


class DefaultSearcher(Searcher):

    def __init__(self, composed_retriever: Retriever, mapper: SourceDocumentMapper, error_messages: ErrorMessages):
        self._composed_retriever = composed_retriever
        self._mapper = mapper
        self.error_messages = error_messages

    def search(self, search_request: SearchRequest) -> SearchResponse:

        retrieved_documents = ...
        search_metadata = {meta.key: meta.value for meta in search_request.metadata} if search_request.metadata else {}
        config = RunnableConfig(metadata={"filter_kwargs": search_metadata})
        try:
            retrieved_documents = self._composed_retriever.invoke(input=search_request.search_term, config=config)
        except NoOrEmptyCollectionError:
            logger.warning("No documents available in vector database.")
            return SearchResponse(
                ChatResponse(answer=self.error_messages.no_or_empty_collection, finish_reason="Error", citations=[])
            )
        except Exception as e:
            logger.error("Error while searching for documents in vector database: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error while searching for documents in vector database: %s" % e,
            )

        source_documents = [
            self._mapper.langchain_document2source_document(document)
            for document in retrieved_documents
            if document.metadata.get("type", None) != ContentType.SUMMARY.value
        ]

        return SearchResponse(SourceDocuments(documents=source_documents))
