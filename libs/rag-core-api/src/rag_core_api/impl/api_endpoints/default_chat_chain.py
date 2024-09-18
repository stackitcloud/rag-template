import logging
from typing import Any, Optional

from fastapi import HTTPException, status
from langchain_core.runnables import RunnableConfig
from langchain_core.documents import Document

from rag_core_api.models.search_request import SearchRequest
from rag_core_api.models.chat_history import ChatHistory
from rag_core_api.impl.mapper.source_document_mapper import SourceDocumentMapper
from rag_core_api.models.chat_request import ChatRequest
from rag_core_api.models.chat_response import ChatResponse
from rag_core_api.models.source_documents import SourceDocuments
from rag_core_api.retriever.retriever import Retriever
from rag_core_api.api_endpoints.chat_chain import ChatChain
from rag_core_api.api_endpoints.searcher import Searcher
from rag_core_api.impl.answer_generation_chains.answer_chain_input_data import AnswerChainInputData
from rag_core_api.impl.answer_generation_chains.answer_generation_chain import AnswerGenerationChain
from rag_core_api.impl.answer_generation_chains.rephrasing_chain import RephrasingChain
from rag_core_api.impl.answer_generation_chains.rephrasing_chain_input_data import RephrasingChainInputData
from rag_core_api.impl.settings.error_messages import ErrorMessages


logger = logging.getLogger(__name__)


class DefaultChatChain(ChatChain):

    def __init__(
        self,
        composed_retriever: Retriever,
        answer_generation_chain: AnswerGenerationChain,
        rephrasing_chain: RephrasingChain,
        searcher: Searcher,
        mapper: SourceDocumentMapper,
        error_messages: ErrorMessages,
    ):
        self._composed_retriever = composed_retriever
        self._answer_generation_chain = answer_generation_chain
        self._searcher = searcher
        self._mapper = mapper
        self._rephrasing_chain = rephrasing_chain
        self.error_messages = error_messages

    async def ainvoke(
        self, chain_input: ChatRequest, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> ChatResponse:
        current_question = chain_input.message
        history = chain_input.history if chain_input.history else ChatHistory(messages=[])

        logger.info(
            "RECEIVED question: %s",
            current_question,
        )

        rephrasing_input = RephrasingChainInputData(
            question=chain_input.message, history="\n".join([f"{x.role}: {x.message}" for x in history.messages])
        )

        rephrased_question = await self._rephrasing_chain.ainvoke(chain_input=rephrasing_input, config=config)

        retrieved_documents = self._searcher.search(
            search_request=SearchRequest(search_term=rephrased_question)
        ).actual_instance

        if not isinstance(retrieved_documents, SourceDocuments):
            # failure in search. Forward error
            return retrieved_documents

        retrieved_langchain_documents = [
            self._mapper.source_document2langchain_document(x) for x in retrieved_documents.documents
        ]

        if not retrieved_langchain_documents:
            return ChatResponse(answer=self.error_messages.no_documents_message, citations=[], finish_reason="")

        answer_generation_input = AnswerChainInputData(
            question=chain_input.message,
            retrieved_documents=retrieved_langchain_documents,
            history="\n".join([f"{x.role}: {x.message}" for x in history.messages]),
        )

        answer = await self._answer_generation_chain.ainvoke(answer_generation_input, config)

        logger.info("GENERATED answer: %s", answer)

        return ChatResponse(
            answer=answer, citations=retrieved_documents.documents, finish_reason=""
        )  # TODO: get finish_reason. Might be impossible/difficult depending on used llm

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
