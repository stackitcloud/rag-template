"""Module for the string enum class GraphNodeNames and the DefaultChatGraph class."""

import io
import logging
from enum import StrEnum
from functools import partial
from pathlib import Path
from time import time
from typing import Any, Optional

from fastapi import HTTPException, status
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.graph import MermaidDrawMethod
from langgraph.graph import END, START, StateGraph
from PIL import Image

from rag_core_api.graph.graph_base import GraphBase
from rag_core_api.impl.answer_generation_chains.answer_generation_chain import (
    AnswerGenerationChain,
)
from rag_core_api.impl.answer_generation_chains.rephrasing_chain import RephrasingChain
from rag_core_api.impl.graph.graph_state.graph_state import AnswerGraphState
from rag_core_api.impl.retriever.no_or_empty_collection_error import (
    NoOrEmptyCollectionError,
)
from rag_core_api.impl.settings.chat_history_settings import ChatHistorySettings
from rag_core_api.impl.settings.error_messages import ErrorMessages
from rag_core_api.mapper.information_piece_mapper import InformationPieceMapper
from rag_core_api.models.chat_request import ChatRequest
from rag_core_api.models.chat_response import ChatResponse
from rag_core_api.models.content_type import ContentType
from rag_core_api.retriever.retriever import Retriever

logger = logging.getLogger(__name__)


class GraphNodeNames(StrEnum):
    """
    GraphNodeNames is an enumeration of different types of graph nodes used in the chat graph.

    Attributes
    ----------
    REPHRASE : str
        Represents a node that rephrases the question.
    RETRIEVE : str
        Represents a node that retrieves the relevant langchain documents from the vectordatabase.
    GENERATE : str
        Represents a node that generates the response.
    ERROR_NODE : str
        Represents a node that handles errors.
    """

    REPHRASE = "rephrase"
    RETRIEVE = "retrieve"
    GENERATE = "generate"
    ERROR_NODE = "error_node"


class DefaultChatGraph(GraphBase):
    """The DefaultChatGraph handles chat requests.

    It utilizes various chains and retrievers to process and generate responses based on the input message and chat
    history.
    """

    def __init__(
        self,
        answer_generation_chain: AnswerGenerationChain,
        rephrasing_chain: RephrasingChain,
        composed_retriever: Retriever,
        mapper: InformationPieceMapper,
        error_messages: ErrorMessages,
        chat_history_settings: ChatHistorySettings,
    ):
        """
        Initialize the DefaultChatGraph.

        Parameters
        ----------
        answer_generation_chain : AnswerGenerationChain
            The chain responsible for generating answers.
        rephrasing_chain : RephrasingChain
            The chain responsible for rephrasing questions.
        composed_retriever : Retriever
            The retriever used to fetch relevant information.
        mapper : InformationPieceMapper
            The mapper used to map information pieces.
        error_messages : ErrorMessages
            The error messages to be used in case of failures.
        chat_history_settings : ChatHistorySettings
            The settings for managing chat history.
        """
        self._state_graph = StateGraph(AnswerGraphState)
        self._answer_generation_chain = answer_generation_chain
        self._composite_retriever = composed_retriever
        self._mapper = mapper
        self._chat_history_settings = chat_history_settings
        self._rephrasing_chain = rephrasing_chain
        self._error_messages = error_messages
        self._rephrase_node_builder = partial(self._rephrase_node)
        self._generate_node_builder = partial(self._generate_node)
        self._graph = self._setup_graph()

    async def ainvoke(
        self, graph_input: ChatRequest, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> ChatResponse:
        """
        Asynchronously invokes the chat graph with the provided input and configuration.

        Parameters
        ----------
        graph_input : ChatRequest
            The input data for the chat graph, including the message and history.
        config : Optional[RunnableConfig]
            Configuration options for the invocation (default None).
        **kwargs : Any
            Additional keyword arguments.

        Returns
        -------
        ChatResponse
            The response from the chat graph.

        Notes
        -----
        - The method processes the chat history based on the settings defined in `_chat_history_settings`.
        - The history is formatted and included in the `AnswerGraphState`.
        """
        if not graph_input.message.strip():
            return ChatResponse(
                answer=self._error_messages.empty_message,
                citations=[],
                finish_reason=self._error_messages.empty_message,
            )

        history_of_interest = []
        if graph_input.history and graph_input.history.messages:
            history_of_interest = graph_input.history.messages[-self._chat_history_settings.limit :]
            if self._chat_history_settings.reverse:
                pairs = list(zip(history_of_interest[::2], history_of_interest[1::2]))
                reversed_pairs = pairs[::-1]
                history_of_interest = [item for sublist in reversed_pairs for item in sublist]
        history = "\n".join([f"{x.role}: {x.message}" for x in history_of_interest])
        state = AnswerGraphState.create(
            question=graph_input.message,
            history=history,
            error_messages=[],
            finish_reasons=[],
            information_pieces=[],
            langchain_documents=[],
        )

        logger.info(
            "RECEIVED question: %s",
            state["question"],
        )

        response_state = await self._graph.ainvoke(input=state, config=config)

        logger.info("GENERATED answer: %s", response_state["response"].answer)

        return response_state["response"]

    def draw_graph(self, relative_dir_path: Optional[str] = None) -> None:
        """
        Draw the graph and save it as a PNG file.

        Parameters
        ----------
        relative_dir_path : Optional[str]
            The relative directory path where the PNG file will be saved.
            If not provided, the current working directory will be used.
            (default None)

        Returns
        -------
        None
        """
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
            citations=state["information_pieces"],
            finish_reason="",  # TODO: get finish_reason. Might be impossible/difficult depending on used llm
        )
        return {"answer_text": answer_text, "response": chat_response}

    async def _retrieve_node(self, state: dict) -> dict:
        try:
            retrieved_documents = await self._composite_retriever.ainvoke(retriever_input=state["rephrased_question"])
        except NoOrEmptyCollectionError:
            logger.warning("No or empty collection encountered.")
            return {
                self.ERROR_MESSAGES_KEY: [self._error_messages.no_or_empty_collection],
                self.FINISH_REASONS: ["NoOrEmptyCollectionError"],
            }
        except Exception as e:
            logger.error("Error while searching for documents in vector database: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error while searching for documents in vector database: %s" % e,
            )

        response = {}
        if not retrieved_documents:
            response[self.ERROR_MESSAGES_KEY] = [self._error_messages.no_documents_message]
            response[self.FINISH_REASONS] = ["No documents found"]
            return response

        information_pieces = [
            self._mapper.langchain_document2information_piece(document)
            for document in retrieved_documents
            if document.metadata.get("type", ContentType.SUMMARY.value) != ContentType.SUMMARY.value
        ]

        response["information_pieces"] = information_pieces
        response["langchain_documents"] = retrieved_documents

        return response

    async def _error_node(self, state: dict) -> dict:
        error_message = " ".join(set(state[self.ERROR_MESSAGES_KEY]))
        finish_reson = " ".join(set(state[self.FINISH_REASONS]))
        return {"response": ChatResponse(answer=error_message, citations=[], finish_reason=finish_reson)}

    #####################
    # conditional edges #
    #####################
    def _docs_retrieved_edge(self, state: dict) -> str:
        if state["information_pieces"]:
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
