from asyncio import run
import logging
from threading import Thread

from fastapi import Depends
from dependency_injector.wiring import Provide, inject
from langchain_core.runnables import RunnableConfig

from rag_core_api.impl.graph_state.graph_state import AnswerGraphState
from rag_core_api.impl.settings.chat_history_settings import ChatHistorySettings
from rag_core_api.models.chat_request import ChatRequest
from rag_core_api.models.chat_response import ChatResponse
from rag_core_api.models.delete_request import DeleteRequest
from rag_core_api.models.search_request import SearchRequest
from rag_core_api.models.search_response import SearchResponse
from rag_core_api.models.upload_source_document import UploadSourceDocument
from rag_core_api.api_endpoints.chat_graph import ChatGraph
from rag_core_api.api_endpoints.searcher import Searcher
from rag_core_api.api_endpoints.source_documents_remover import SourceDocumentsRemover
from rag_core_api.api_endpoints.source_documents_uploader import SourceDocumentsUploader
from rag_core_api.dependency_container import DependencyContainer
from rag_core_api.apis.rag_api_base import BaseRagApi
from rag_core_api.evaluator.evaluator import Evaluator


logger = logging.getLogger(__name__)


class RagApi(BaseRagApi):

    def __init__(self):
        super().__init__()
        self._background_threads = []

    @inject
    async def chat(
        self,
        session_id: str,
        chat_request: ChatRequest,
        chat_graph: ChatGraph = Depends(Provide[DependencyContainer.traced_chat_graph]),
        chat_history_config: ChatHistorySettings = Depends(Provide[DependencyContainer.chat_history_config]),
    ) -> ChatResponse:
        config = RunnableConfig(
            tags=[],
            callbacks=None,
            recursion_limit=25,
            metadata={"session_id": session_id},
        )
        history_of_interest = chat_request.history.messages[-chat_history_config["limit"] :]
        if chat_history_config["reverse"]:
            paris = list(zip(history_of_interest[::2], history_of_interest[1::2]))
            reversed_paris = paris[::-1]
            history_of_interest = [item for sublist in reversed_paris for item in sublist]
        history = "\n".join([f"{x.role}: {x.message}" for x in history_of_interest])
        state = AnswerGraphState(
            question=chat_request.message,
            rephrased_question=None,
            history=history,
            source_documents=None,
            answer_text=None,
            response=None,
            retries=0,
            is_harmful=True,
            is_from_context=False,
            answer_is_relevant=False,
        )
        return await chat_graph.ainvoke(state, config)

    @inject
    async def evaluate(
        self,
        evaluator: Evaluator = Depends(Provide[DependencyContainer.evaluator]),
    ) -> None:
        # cleanup threads
        self._background_threads = [t for t in self._background_threads if t.is_alive()]
        thread = Thread(target=lambda: run(evaluator.aevaluate()))
        thread.start()
        self._background_threads.append(thread)

    @inject
    async def remove_source_documents(
        self,
        delete_request: DeleteRequest,
        source_documents_remover: SourceDocumentsRemover = Depends(
            Provide[DependencyContainer.source_documents_remover]
        ),
    ) -> None:
        source_documents_remover.remove_source_documents(delete_request)

    @inject
    async def search(
        self,
        search_request: SearchRequest,
        searcher: Searcher = Depends(Provide[DependencyContainer.searcher]),
    ) -> SearchResponse:
        return searcher.search(search_request)

    @inject
    async def upload_source_documents(
        self,
        upload_source_document: list[UploadSourceDocument],
        source_documents_uploader: SourceDocumentsUploader = Depends(
            Provide[DependencyContainer.source_documents_uploader]
        ),
    ) -> None:
        source_documents_uploader.upload_source_documents(upload_source_document)
