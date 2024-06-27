import logging

from fastapi import HTTPException, status
from langchain_core.runnables import RunnableConfig

from rag_core.api_endpoints.searcher import Searcher
from rag_core.impl.mapper.source_document_mapper import SourceDocumentMapper
from rag_core.models.chat_response import ChatResponse
from rag_core.models.content_type import ContentType
from rag_core.models.search_request import SearchRequest
from rag_core.models.search_response import SearchResponse
from rag_core.retriever.retriever import Retriever
from rag_core.impl.retriever.no_or_empty_collection_error import NoOrEmptyCollectionError
from rag_core.models.source_documents import SourceDocuments


logger = logging.getLogger(__name__)


class DefaultSearcher(Searcher):

    def __init__(self, composed_retriever: Retriever, mapper: SourceDocumentMapper):
        self._composed_retriever = composed_retriever
        self._mapper = mapper

    def search(self, search_request: SearchRequest) -> SearchResponse:

        retrieved_documents = ...
        search_metadata = {meta.key: meta.value for meta in search_request.metadata}
        config = RunnableConfig(metadata={"filter_kwargs": search_metadata})
        try:
            retrieved_documents = self._composed_retriever.invoke(input=search_request.search_term, config=config)
        except NoOrEmptyCollectionError:
            logger.warning("No documents available in vector database.")
            return ChatResponse(answer="Nix da an Dokumenten!", finish_reason="Error", citations=[])
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
