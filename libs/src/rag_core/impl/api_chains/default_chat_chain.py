import logging
from typing import Any, Optional

from fastapi import HTTPException, status
from langchain_core.runnables import RunnableConfig
from langchain_core.documents import Document

from rag_core.api_chains.chat_chain import ChatChain
from rag_core.impl.answer_generation_chains.answer_chain_input_data import AnswerChainInputData
from rag_core.impl.answer_generation_chains.answer_generation_chain import AnswerGenerationChain
from rag_core.models.chat_request import ChatRequest
from rag_core.models.chat_response import ChatResponse
from rag_core.retriever.retriever import Retriever


logger = logging.getLogger(__name__)


class DefaultChatChain(ChatChain):

    def __init__(self, composed_retriever: Retriever, answer_generation_chain: AnswerGenerationChain):
        self._composed_retriever = composed_retriever
        self._answer_generation_chain = answer_generation_chain

    def invoke(self, input: ChatRequest, config: Optional[RunnableConfig] = None, **kwargs: Any) -> ChatResponse:

        # TODO: use the chat history for something ]:->
        chat_history = input.history
        current_question = input.message

        logger.info(
            "RECEIVED question: %s",
            current_question,
        )

        retrieved_documents = self._search_documents(
            prompt=current_question, composed_retriever=self._composed_retriever
        )  # TODO: apply filter quarks as needed. For now, we just search for all documents.

        answer_generation_input = AnswerChainInputData(question=input.message, retrieved_documents=retrieved_documents)

        answer = self._answer_generation_chain.invoke(answer_generation_input, config)

        logger.info("GENERATED answer: %s", answer)

        response = ChatResponse(answer=answer, citations=[], finish_reason="")
        return response

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
