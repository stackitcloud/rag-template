import json
import logging
from typing import ClassVar, Dict, List, Tuple  # noqa: F401
from fastapi import Depends, HTTPException, status
from langchain_core.runnables import RunnableConfig
from dependency_injector.wiring import Provide, inject
from langchain_core.documents import Document

from fastapi import Depends, HTTPException
from rag_core.api_chains.chat_chain import ChatChain
from rag_core.dependency_container import DependencyContainer
from rag_core.impl.answer_generation_chains.answer_chain_input_data import AnswerChainInputData
from rag_core.impl.retriever.no_or_empty_collection_error import NoOrEmptyCollectionError
from rag_core.retriever.retriever import Retriever
from rag_core.models.chat_request import ChatRequest
from rag_core.models.chat_response import ChatResponse
from rag_core.models.delete_request import DeleteRequest
from rag_core.models.search_request import SearchRequest
from rag_core.models.search_response import SearchResponse
from rag_core.models.upload_source_document import UploadSourceDocument
from rag_core.apis.rag_api_base import BaseRagApi

from rag_core.impl.answer_generation_chains.answer_generation_chain import AnswerGenerationChain
from rag_core.impl.answer_generation_chains.answer_chain_input_data import AnswerChainInputData
from rag_core.retriever.retriever import Retriever
from rag_core.apis.rag_api_base import BaseRagApi
from rag_core.models.chat_request import ChatRequest
from rag_core.models.chat_response import ChatResponse
from rag_core.models.upload_source_document import UploadSourceDocument
from rag_core.models.delete_request import DeleteRequest
from rag_core.models.search_request import SearchRequest
from rag_core.models.source_document import SourceDocument
from rag_core.models.source_documents import SourceDocuments
from rag_core.vector_databases.vector_database import VectorDatabase
from rag_core.impl.mapper.upload_source_document2langchain_document import (
    UploadSourceDocument2LangchainDocument,
)
from rag_core.models.search_response import SearchResponse


logger = logging.getLogger(__name__)


class RagApi(BaseRagApi):

    @inject
    def chat(
        self,
        session_id: str,
        chat_request: ChatRequest,
        chat_chain: ChatChain = Depends(Provide[DependencyContainer.chat_chain]),
    ) -> ChatResponse:
        config = {"session_id": session_id}
        return chat_chain.invoke(chat_request, config)

    @inject
    def remove_source_documents(
        self,
        delete_request: DeleteRequest,
        vector_database: VectorDatabase = Depends(Provide[DependencyContainer.vector_database]),
    ) -> None:
        logger.info("Deleting documents from vector database")
        try:
            vector_database.delete(delete_request.metadata)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Error while deleting %s from vector db" % json.dumps(delete_request.metadata),
            )
        # TODO implement the other configured error codes :D

    @inject
    def search(
        self,
        search_request: SearchRequest,
        composed_retriever: Retriever = Depends(Provide[DependencyContainer.composed_retriever]),
    ) -> SearchResponse:
        try:
            composed_retriever.verify_readiness()
        except NoOrEmptyCollectionError:
            logger.warning("No documents available in vector database.")
            return ChatResponse(answer="Nix da an Dokumenten!", finish_reason="Error", citations=[])

        retrieved_documents = ...
        config = RunnableConfig(metadata=search_request.metadata)
        try:
            retrieved_documents = composed_retriever.invoke(input=search_request.search_term, config=config)
        except Exception as e:
            logger.error("Error while searching for documents in vector database: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error while searching for documents in vector database: %s" % e,
            )

        source_documents = [
            SourceDocument(content=document.page_content, metadata=document.metadata)
            for document in retrieved_documents
            if document.metadata.get("type", None) != "summary"
        ]

        return SearchResponse(source_documents=SourceDocuments(source_documents=source_documents))

    @inject
    def upload_source_documents(
        self,
        upload_source_document: List[UploadSourceDocument],
        vector_database: VectorDatabase = Depends(Provide[DependencyContainer.vector_database]),
    ) -> None:
        langchain_documents = [
            UploadSourceDocument2LangchainDocument.source_document2langchain_document(document)
            for document in upload_source_document
        ]
        try:
            # TODO: maybe put in background task. Just writing to the database should not take so incredibly long (for moderate number of documents). If more users are using the system and upload in parallel, we should think, how to handle that best.
            vector_database.upload(langchain_documents)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def _search_documents(self, prompt: str, composed_retriever: Retriever, metadata: dict = None) -> list[Document]:
        config = RunnableConfig(metadata=metadata)
        try:
            retrieved_documents = composed_retriever.invoke(input=prompt, config=config)
        except Exception as e:
            logger.error("Error while searching for documents in vector database: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error while searching for documents in vector database: %s" % e,
            )
        return retrieved_documents
