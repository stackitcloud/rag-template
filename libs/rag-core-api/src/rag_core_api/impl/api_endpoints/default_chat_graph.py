import logging
from typing import Any, Optional, Sequence
from functools import partial
from enum import StrEnum

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

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
    SAFE_GUARD = "safe_guard"
    RETRIEVE = "retrieve"
    GENERATE = "generate"
    ANSWER_RELEVANCY = "answer_relevancy"
    ANSWER_FROM_CONTEXT = "answer_from_context"
    ANSWER_CHECK_SINK = "answer_check_sink"
    INCREMENT_RETRIES = "increment_retries"
    ERROR_NODE = "error_node"
    GENERATE_SINK = "generate_sink"


class DefaultChatGraph(ChatGraph):

    RETRY_LIMIT = 3

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
        self._safe_guard_chain = None  # TODO: add safe guard
        self._anwer_relevancy_chain = None  # TODO: add answer relevancy chain
        self._answer_from_context_chain = None  # TODO: add answer from context chain
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

    async def _is_harmful_node(self, state: dict) -> dict:
        # TODO
        response = {"is_harmful": False}
        if response["is_harmful"]:
            response["error_messages"] = [self.error_messages.harmful_question]
            response["finish_reasons"] = ["Harmful question"]
        return response

    async def _retrieve_node(self, state: dict) -> dict:
        retrieved_documents = self._searcher.search(
            search_request=SearchRequest(search_term=state["rephrased_question"])
        ).actual_instance

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

    async def _answer_relevancy_node(self, state: dict) -> dict:
        # TODO
        return {"answer_is_relevant": True}

    async def _answer_from_context_node(self, state: dict) -> dict:
        # TODO add answer from context logic
        return {"is_from_context": True}

    async def _increment_retries_node(self, state: dict) -> dict:
        response = {"retries": state["retries"] + 1}
        if response["retries"] > self.RETRY_LIMIT:
            response["error_message"] = [self.error_messages.no_answer_found]
            response["finish_reason"] = ["Maximum retries exceeded, no answer found"]
        return response

    async def _sink_node(self, state: dict) -> dict:
        return state

    async def _error_node(self, state: dict) -> dict:
        error_message = " ".join(state["error_messages"])
        finish_reson = " ".join(state["finish_reasons"])
        return {"response": ChatResponse(answer=error_message, citations=[], finish_reason=finish_reson)}

    async def _generate_sink_node(self, state: dict) -> dict:
        return state

    #####################
    # conditional edges #
    #####################
    def _docs_retrieved_edge(self, state: dict) -> str:
        if state["source_documents"]:
            return GraphNodeNames.GENERATE
        return GraphNodeNames.ERROR_NODE

    def _decide_if_harmful_edge(self, state: dict) -> Sequence[str]:
        if state["is_harmful"]:
            return [GraphNodeNames.ERROR_NODE]
        return [GraphNodeNames.ANSWER_RELEVANCY, GraphNodeNames.ANSWER_FROM_CONTEXT]

    def _question_answered_and_from_context_edge(self, state: dict) -> str:
        if state["answer_is_relevant"] and state["is_from_context"]:
            return END
        return GraphNodeNames.INCREMENT_RETRIES

    def _retries_exceeded_edge(self, state: dict) -> str:
        if state["error_messages"]:
            return GraphNodeNames.ERROR_NODE
        return GraphNodeNames.REPHRASE

    def _add_nodes(self):
        self._state_graph.add_node(GraphNodeNames.REPHRASE, self._rephrase_node_builder)
        self._state_graph.add_node(GraphNodeNames.SAFE_GUARD, self._is_harmful_node)
        self._state_graph.add_node(GraphNodeNames.RETRIEVE, self._retrieve_node)
        self._state_graph.add_node(GraphNodeNames.GENERATE, self._generate_node_builder)
        self._state_graph.add_node(GraphNodeNames.GENERATE_SINK, self._generate_sink_node)
        self._state_graph.add_node(GraphNodeNames.ANSWER_RELEVANCY, self._answer_relevancy_node)
        self._state_graph.add_node(GraphNodeNames.ANSWER_FROM_CONTEXT, self._answer_from_context_node)
        self._state_graph.add_node(GraphNodeNames.ANSWER_CHECK_SINK, self._sink_node)
        self._state_graph.add_node(GraphNodeNames.INCREMENT_RETRIES, self._increment_retries_node)
        self._state_graph.add_node(GraphNodeNames.ERROR_NODE, self._error_node)

    def _wire_graph(self):
        self._state_graph.add_edge(START, GraphNodeNames.REPHRASE)
        self._state_graph.add_edge(START, GraphNodeNames.SAFE_GUARD)
        self._state_graph.add_edge(GraphNodeNames.REPHRASE, GraphNodeNames.RETRIEVE)

        self._state_graph.add_conditional_edges(
            GraphNodeNames.RETRIEVE, self._docs_retrieved_edge, [GraphNodeNames.GENERATE, GraphNodeNames.ERROR_NODE]
        )

        self._state_graph.add_edge([GraphNodeNames.GENERATE, GraphNodeNames.SAFE_GUARD], GraphNodeNames.GENERATE_SINK)

        successors = [GraphNodeNames.ERROR_NODE, GraphNodeNames.ANSWER_RELEVANCY, GraphNodeNames.ANSWER_FROM_CONTEXT]
        self._state_graph.add_conditional_edges(GraphNodeNames.GENERATE_SINK, self._decide_if_harmful_edge, successors)

        self._state_graph.add_edge(successors[1:], GraphNodeNames.ANSWER_CHECK_SINK)

        self._state_graph.add_conditional_edges(
            GraphNodeNames.ANSWER_CHECK_SINK,
            self._question_answered_and_from_context_edge,
            [GraphNodeNames.INCREMENT_RETRIES, END],
        )

        self._state_graph.add_conditional_edges(
            GraphNodeNames.INCREMENT_RETRIES,
            self._retries_exceeded_edge,
            [GraphNodeNames.REPHRASE, GraphNodeNames.ERROR_NODE],
        )
        self._state_graph.add_edge(GraphNodeNames.ERROR_NODE, END)
