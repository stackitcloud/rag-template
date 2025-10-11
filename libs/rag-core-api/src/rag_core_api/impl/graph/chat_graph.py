"""Module for the string enum class GraphNodeNames and the DefaultChatGraph class."""

import io
import logging
from enum import StrEnum
import unicodedata
from functools import partial
from pathlib import Path
from time import time
from typing import Any, Optional

import langdetect
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
from rag_core_api.impl.answer_generation_chains.evaluation_chain import EvaluationChain
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
    DETERMINE_LANGUAGE : str
        Reperesents a node that determiens the language of the question.
    REPHRASE : str
        Represents a node that rephrases the question.
    RETRIEVE : str
        Represents a node that retrieves the relevant langchain documents from the vectordatabase.
    GENERATE : str
        Represents a node that generates the response.
    ERROR_NODE : str
        Represents a node that handles errors.
    """

    DETERMINE_LANGUAGE = "determine_language"
    REPHRASE = "rephrase"
    RETRIEVE = "retrieve"
    GENERATE = "generate"
    EVALUATE = "evaluate"
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
        evaluation_chain: EvaluationChain,
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
        self._evaluation_chain = evaluation_chain
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
            filters=(graph_input.filters.to_dict() if getattr(graph_input, "filters", None) else None),
        )

        logger.info(
            "RECEIVED question: %s",
            state["question"],
        )

        # Ensure config has metadata container
        if config is None:
            config = RunnableConfig(metadata={})
        elif config.get("metadata") is None:
            config["metadata"] = {}
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
    @staticmethod
    def _sanitize_document_name(document_name: str) -> str:
        """Sanitize a document name to match ingestion rules.

        Applies the same normalization as the admin uploader:
        - transliterate ä->ae, ö->oe, ü->ue, ß->ss
        - keep only alphanumeric characters, underscores, and periods
        """
        translit = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}
        for char, replacement in translit.items():
            document_name = document_name.replace(char, replacement)
        document_name = "".join(
            c for c in unicodedata.normalize("NFKD", document_name) if c.isalnum() or c in {"_", "."}
        )
        return document_name

    async def _determine_language_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:
        question = state["question"]
        question_language = langdetect.detect(question)
        logger.debug('Detected langauge for question "%s": %s', question, question_language)
        return {"language": question_language}

    async def _rephrase_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:
        rephrased_question = await self._rephrasing_chain.ainvoke(chain_input=state, config=config)
        # Ensure rephrased_question is a string
        if hasattr(rephrased_question, "content"):
            rephrased_question = rephrased_question.content
        elif not isinstance(rephrased_question, str):
            rephrased_question = str(rephrased_question)
        return {"rephrased_question": rephrased_question}

    async def _generate_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:
        answer_text = await self._answer_generation_chain.ainvoke(state, config)
        if hasattr(answer_text, "content"):
            answer_text = answer_text.content
        elif not isinstance(answer_text, str):
            answer_text = str(answer_text)
        chat_response = ChatResponse(
            answer=answer_text,
            citations=state["information_pieces"],
            finish_reason="",  # TODO: get finish_reason. Might be impossible/difficult depending on used llm
        )
        return {"answer_text": answer_text, "response": chat_response}

    async def _evaluate_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:
        """LLM-based helpfulness check. Decides whether to accept the answer or re-retrieve from LBO.

        Input to the evaluator includes: question, answer, rephrased_question and a short context summary.
        """
        evaluator_input = {
            "question": state.get("question", ""),
            "rephrased_question": state.get("rephrased_question", ""),
            "answer": state.get("answer_text", ""),
            # Keep the evaluator prompt lean: feed the first 3 snippet heads
            "context": "\n\n".join([doc.page_content[:500] for doc in state.get("langchain_documents", [])][:3]),
            "instruction": (
                "Bewerte, ob die Antwort hilfreich ist, um die Nutzerfrage zu beantworten. "
                "Antworte ausschließlich mit 'yes' oder 'no'."
            ),
        }
        helpful = await self._evaluation_chain.ainvoke(evaluator_input, config=config)

        update: dict[str, Any] = {"additional_info": {"helpful": bool(helpful)}}
        if not helpful and state.get("filters") and state["filters"].get("lbo"):
            # Switch active filter to LBO for the next retrieval round
            new_filters = dict(state["filters"])  # shallow copy
            new_filters["active_files"] = state["filters"]["lbo"]
            update["filters"] = new_filters
            # Overwrite retrieval artifacts to avoid aggregating B-Plan and LBO sources
            update["information_pieces"] = []
            update["langchain_documents"] = []
        return update

    async def _retrieve_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:
        try:
            # Apply filters if present: prefer bebauungsplan list by default; can switch to lbo on retry
            metadata_filters = {}
            if state.get("filters") and isinstance(state["filters"], dict):
                # This node will respect filters passed within config.metadata.filter_kwargs as 'file_name'
                # We map group list to a generic 'file_name' filter here if present
                filenames = state["filters"].get("active_files") or state["filters"].get("bebauungsplan")
                if filenames:
                    if isinstance(filenames, list):
                        sanitized = [self._sanitize_document_name(f) for f in filenames]
                    else:
                        sanitized = [self._sanitize_document_name(filenames)]
                    metadata_filters["file_name"] = sanitized

            effective_config = config or RunnableConfig(metadata={})
            meta = effective_config.get("metadata", {})
            current_filters = meta.get("filter_kwargs", {})
            meta["filter_kwargs"] = {**current_filters, **metadata_filters}
            effective_config["metadata"] = meta

            retrieved_documents = await self._composite_retriever.ainvoke(
                retriever_input=state["rephrased_question"], config=effective_config
            )
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
            # If this is the first run and LBO filters are available, schedule a retry with LBO
            filters: dict | None = state.get("filters") if isinstance(state.get("filters"), dict) else None
            already_retried = bool(state.get("retry_retrieve"))
            lbo_files = (filters or {}).get("lbo") if filters else None
            if (not already_retried) and lbo_files:
                new_filters = dict(filters)
                new_filters["active_files"] = lbo_files
                response["filters"] = new_filters
                response["retry_retrieve"] = True
                # Clear artifacts to ensure a clean second pass
                response["information_pieces"] = []
                response["langchain_documents"] = []
                return response
            # Otherwise, fail to error node and clear retry flag
            response[self.ERROR_MESSAGES_KEY] = [self._error_messages.no_documents_message]
            response[self.FINISH_REASONS] = ["No documents found"]
            response["retry_retrieve"] = False
            return response

        information_pieces = [
            self._mapper.langchain_document2information_piece(document)
            for document in retrieved_documents
            if document.metadata.get("type", ContentType.SUMMARY.value) != ContentType.SUMMARY.value
        ]

        # Replace instead of aggregate to avoid mixing first and second pass results
        response["information_pieces"] = information_pieces
        response["langchain_documents"] = retrieved_documents
        # Ensure any previous retry flag is cleared after a successful retrieval
        if state.get("retry_retrieve"):
            response["retry_retrieve"] = False
            # Mark that this was a second pass; skip evaluation and end after generation
            response["skip_evaluate"] = True
        else:
            response["skip_evaluate"] = False

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
        # If a retry has been scheduled (switch to LBO), loop back to RETRIEVE once
        if state.get("retry_retrieve"):
            return GraphNodeNames.RETRIEVE
        return GraphNodeNames.ERROR_NODE

    def _add_nodes(self):
        self._state_graph.add_node(GraphNodeNames.DETERMINE_LANGUAGE, self._determine_language_node)
        self._state_graph.add_node(GraphNodeNames.REPHRASE, self._rephrase_node_builder)
        self._state_graph.add_node(GraphNodeNames.RETRIEVE, self._retrieve_node)
        self._state_graph.add_node(GraphNodeNames.GENERATE, self._generate_node_builder)
        self._state_graph.add_node(GraphNodeNames.EVALUATE, self._evaluate_node)
        self._state_graph.add_node(GraphNodeNames.ERROR_NODE, self._error_node)

    def _wire_graph(self):
        self._state_graph.add_edge(START, GraphNodeNames.REPHRASE)
        self._state_graph.add_edge(START, GraphNodeNames.DETERMINE_LANGUAGE)
        self._state_graph.add_edge(
            [GraphNodeNames.REPHRASE, GraphNodeNames.DETERMINE_LANGUAGE], GraphNodeNames.RETRIEVE
        )
        self._state_graph.add_conditional_edges(
            GraphNodeNames.RETRIEVE,
            self._docs_retrieved_edge,
            [GraphNodeNames.GENERATE, GraphNodeNames.ERROR_NODE, GraphNodeNames.RETRIEVE],
        )
        # After generation, evaluate; if unhelpful, switch filters to LBO and re-retrieve+generate
        def evaluate_edge(state: dict) -> str:
            helpful = state.get("additional_info", {}).get("helpful", True)
            return END if helpful else GraphNodeNames.RETRIEVE

        # If we marked to skip evaluation (successful second pass), end after GENERATE; otherwise go to EVALUATE
        def after_generate_edge(state: dict) -> str:
            return END if state.get("skip_evaluate") else GraphNodeNames.EVALUATE

        self._state_graph.add_conditional_edges(
            GraphNodeNames.GENERATE, after_generate_edge, [END, GraphNodeNames.EVALUATE]
        )
        self._state_graph.add_conditional_edges(GraphNodeNames.EVALUATE, evaluate_edge, [END, GraphNodeNames.RETRIEVE])
        self._state_graph.add_edge(GraphNodeNames.ERROR_NODE, END)
        # END wiring complete
