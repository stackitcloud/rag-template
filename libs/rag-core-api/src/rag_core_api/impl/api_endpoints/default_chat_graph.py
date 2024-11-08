import io
import logging
from enum import StrEnum
from functools import partial
from pathlib import Path
from time import time
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.graph import MermaidDrawMethod
from langgraph.graph import END, START, StateGraph
from PIL import Image

from rag_core_api.models.search_request import SearchRequest
from rag_core_api.impl.mapper.source_document_mapper import SourceDocumentMapper
from rag_core_api.models.chat_response import ChatResponse
from rag_core_api.api_endpoints.chat_graph import ChatGraph
from rag_core_api.api_endpoints.searcher import Searcher
from rag_core_api.impl.answer_generation_chains.answer_generation_chain import AnswerGenerationChain
from rag_core_api.impl.answer_generation_chains.rephrasing_chain import RephrasingChain
from rag_core_api.impl.settings.error_messages import ErrorMessages
from rag_core_api.impl.graph_state.graph_state import AnswerGraphState


logger = logging.getLogger(__name__)


class GraphNodeNames(StrEnum):
    REPHRASE = "rephrase"
    RETRIEVE = "retrieve"
    GENERATE = "generate"
    ERROR_NODE = "error_node"


class DefaultChatGraph(ChatGraph):

    def __init__(
        self,
        answer_generation_chain: AnswerGenerationChain,
        rephrasing_chain: RephrasingChain,
        searcher: Searcher,
        mapper: SourceDocumentMapper,
        error_messages: ErrorMessages,
    ):
        self._state_graph = StateGraph(AnswerGraphState)
        self._answer_generation_chain = answer_generation_chain
        self._searcher = searcher
        self._mapper = mapper
        self._rephrasing_chain = rephrasing_chain
        self.error_messages = error_messages
        self._rephrase_node_builder = partial(self._rephrase_node)
        self._generate_node_builder = partial(self._generate_node)
        self._graph = self._setup_graph()

    async def ainvoke(
        self, state: AnswerGraphState, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> ChatResponse:
        logger.info(
            "RECEIVED question: %s",
            state["question"],
        )

        response_state = await self._graph.ainvoke(input=state, config=config)

        logger.info("GENERATED answer: %s", response_state["answer_text"])

        return response_state["response"]

    def draw_graph(self, relative_dir_path: Optional[str] = None) -> None:
        """Draw the graph and save as png."""
        img = Image.open(
            io.BytesIO(
                self._graph.get_graph().draw_mermaid_png(
                    draw_method=MermaidDrawMethod.API,
                )
            )
        )
        if relative_dir_path:
            p = Path.cwd() / relative_dir_path
        else:
            p = Path.cwd()

        p.mkdir(parents=True, exist_ok=True)
        img.save(p / f"graph_{str(time()).replace('.', '_')}.png")

    def _setup_graph(self):
        self._add_nodes()
        self._wire_graph()
        return self._state_graph.compile()

    #########
    # nodes #
    #########
    async def _rephrase_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:
        rephrased_question = await self._rephrasing_chain.ainvoke(chain_input=state, config=config)
        return {"rephrased_question": rephrased_question}

    async def _generate_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:
        answer_text = await self._answer_generation_chain.ainvoke(state, config)
        chat_response = ChatResponse(
            answer=answer_text,
            citations=state["source_documents"],
            finish_reason="",  # TODO: get finish_reason. Might be impossible/difficult depending on used llm
        )
        return {"answer_text": answer_text, "response": chat_response}

    async def _retrieve_node(self, state: dict) -> dict:
        retrieved_documents = self._searcher.search(
            search_request=SearchRequest(search_term=state["rephrased_question"])
        ).actual_instance

        if isinstance(retrieved_documents, ChatResponse):
            # error case; occurs when no or empty collection has been encountered
            return {
                "error_messages": [self.error_messages.no_documents_found, retrieved_documents.answer],
                "finish_reasons": ["No documents found"],
            }

        retrieved_langchain_documents = [
            self._mapper.source_document2langchain_document(x) for x in retrieved_documents.documents
        ]

        response = {
            "source_documents": retrieved_documents.documents,
            "langchain_documents": retrieved_langchain_documents,
        }

        if not response["source_documents"]:
            response["error_messages"] = [self.error_messages.no_documents_found]
            response["finish_reasons"] = ["No documents found"]

        return response

    async def _error_node(self, state: dict) -> dict:
        error_message = " ".join(set(state["error_messages"]))
        finish_reson = " ".join(set(state["finish_reasons"]))
        return {"response": ChatResponse(answer=error_message, citations=[], finish_reason=finish_reson)}

    #####################
    # conditional edges #
    #####################
    def _docs_retrieved_edge(self, state: dict) -> str:
        if state["source_documents"]:
            return GraphNodeNames.GENERATE
        return GraphNodeNames.ERROR_NODE

    def _add_nodes(self):
        self._state_graph.add_node(GraphNodeNames.REPHRASE, self._rephrase_node_builder)
        self._state_graph.add_node(GraphNodeNames.RETRIEVE, self._retrieve_node)
        self._state_graph.add_node(GraphNodeNames.GENERATE, self._generate_node_builder)
        self._state_graph.add_node(GraphNodeNames.ERROR_NODE, self._error_node)

    def _wire_graph(self):
        self._state_graph.add_edge(START, GraphNodeNames.REPHRASE)
        self._state_graph.add_edge(GraphNodeNames.REPHRASE, GraphNodeNames.RETRIEVE)
        self._state_graph.add_conditional_edges(
            GraphNodeNames.RETRIEVE, self._docs_retrieved_edge, [GraphNodeNames.GENERATE, GraphNodeNames.ERROR_NODE]
        )
        self._state_graph.add_edge(GraphNodeNames.GENERATE, END)
        self._state_graph.add_edge(GraphNodeNames.ERROR_NODE, END)
