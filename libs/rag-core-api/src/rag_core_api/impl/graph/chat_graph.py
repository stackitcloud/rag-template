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

    @staticmethod
    def _is_bebauungsplan(doc: Any) -> bool:
        """Detect whether a retrieved document belongs to a local Bebauungsplan.

        Heuristics: checks metadata fields like 'document_url' or 'document' for substrings
        typical of Bebauungspläne (e.g., '/bebauungsplan/' or case-insensitive 'bebauungsplan').
        """
        try:
            meta = getattr(doc, "metadata", {}) or {}
            url = str(meta.get("document_url", ""))
            name = str(meta.get("document", ""))
            joined = f"{url} {name}".lower()
            return "bebauungsplan" in joined
        except Exception:
            return False

    async def _determine_language_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:
        question = state["question"]
        question_language = langdetect.detect(question)
        logger.debug('Detected langauge for question "%s": %s', question, question_language)
        return {"language": question_language}

    async def _rephrase_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:
        # Keep rephrased question identical for now; language is added to state in determine-language node
        return {"rephrased_question": state["question"]}

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
        # If the answer is not helpful, create a concise, proper fallback answer for B-Plan questions
        if not helpful:
            language = state.get("language", "de")
            question = state.get("question", "")
            # Small, safe fallback tailored to Bebauungspläne/Festsetzungen
            if language.startswith("de"):
                fallback = (
                    "Ich konnte aus dem bereitgestellten Kontext keine verlässliche Antwort ableiten. "
                    "Für Fragen zu Bebauungsplänen (B-Plan) und deren Festsetzungen gilt: Innerhalb des Plangebiets "
                    "haben die textlichen und zeichnerischen Festsetzungen des B-Plans Vorrang; die Landesbauordnung (LBO) "
                    "gilt subsidiär, soweit der B‑Plan nichts Abweichendes bestimmt. Bitte geben Sie – wenn möglich – eine konkrete "
                    "Bezeichnung des Bebauungsplans (z. B. Plan‑Name/Nummer) oder Adresse/Flurstück an. Typische Festsetzungen sind u. a.: "
                    "Bauweise/GRZ/GFZ, Baugrenzen/Baulinien, Dachform/Dachneigung, Nutzung und textliche Festsetzungen."
                )
            else:
                fallback = (
                    "I couldn't derive a reliable answer from the provided context. For German local development plans (Bebauungsplan), "
                    "the plan’s textual and graphical stipulations have priority within the plan area; the state building code (LBO) applies "
                    "only where the plan is silent. Please provide the exact plan name/ID or an address/parcel if possible. Typical stipulations "
                    "include e.g. building type, site coverage (GRZ), floor area ratio (GFZ), building lines, roof form/slope, usage, and textual rules."
                )
            chat_response = ChatResponse(
                answer=fallback,
                citations=state.get("information_pieces", []) or [],
                finish_reason="unhelpful_answer_fallback",
            )
            update["answer_text"] = fallback
            update["response"] = chat_response
        return update

    async def _retrieve_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:
        try:
            # Retrieve across all documents; if client provided filters, map to file_name stem list
            effective_config = config or RunnableConfig(metadata={})
            if effective_config.get("metadata") is None:
                effective_config["metadata"] = {}
            # Ensure filter_kwargs exists and set file_name list if provided via filters
            filter_kwargs = dict(effective_config["metadata"].get("filter_kwargs", {}))
            try:
                # Accept both bebauungsplan and lbo lists from state["filters"]
                filters = state.get("filters") or {}
                # The client is expected to pass sanitized stems or raw names; we will re-sanitize on the DB side.
                # Here we only pass through as 'file_name' to be matched.
                active_list = []
                if isinstance(filters, dict):
                    for key in ("active_files", "bebauungsplan", "lbo"):
                        vals = filters.get(key)
                        if vals:
                            if isinstance(vals, list):
                                active_list.extend(vals)
                            else:
                                active_list.append(vals)
                if active_list:
                    # Only pass sanitized stems (without extension)
                    stems = []
                    for v in active_list:
                        base = str(v).rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
                        sanitized = self._sanitize_document_name(base)
                        stem = sanitized[: sanitized.rfind(".")] if "." in sanitized else sanitized
                        stems.append(stem)
                    if stems:
                        filter_kwargs["file_name"] = stems
            except Exception:
                pass
            effective_config["metadata"]["filter_kwargs"] = filter_kwargs

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
            response[self.ERROR_MESSAGES_KEY] = [self._error_messages.no_documents_message]
            response[self.FINISH_REASONS] = ["No documents found"]
            return response

        # Classify into Bebauungsplan vs. LBO/other and keep order within each class
        def is_lbo(doc: Any) -> bool:
            try:
                meta = getattr(doc, "metadata", {}) or {}
                url = str(meta.get("document_url", ""))
                name = str(meta.get("document", ""))
                joined = f"{url} {name}".lower()
                return ("landesbauordnung" in joined) or (" lbo" in joined) or ("/lbo/" in joined) or joined.endswith("lbo.pdf")
            except Exception:
                return False

        bplan_docs = [d for d in retrieved_documents if self._is_bebauungsplan(d)]
        lbo_docs = [d for d in retrieved_documents if is_lbo(d)]
        other_docs = [d for d in retrieved_documents if d not in bplan_docs and d not in lbo_docs]

        # Prioritize for downstream consumers that still look at langchain_documents
        retrieved_documents = [*bplan_docs, *lbo_docs, *other_docs]

        information_pieces = [
            self._mapper.langchain_document2information_piece(document)
            for document in retrieved_documents
            if document.metadata.get("type", ContentType.SUMMARY.value) != ContentType.SUMMARY.value
        ]

        # Replace instead of aggregate
        response["information_pieces"] = information_pieces
        response["langchain_documents"] = retrieved_documents
        response["bplan_documents"] = bplan_docs
        response["lbo_documents"] = lbo_docs
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
            [GraphNodeNames.GENERATE, GraphNodeNames.ERROR_NODE],
        )
        # After generation, always evaluate; on unhelpful answer we generate a proper fallback and end
        def evaluate_edge(state: dict) -> str:
            return END

        # If we marked to skip evaluation (not used anymore), end after GENERATE; otherwise go to EVALUATE
        def after_generate_edge(state: dict) -> str:
            return END if state.get("skip_evaluate") else GraphNodeNames.EVALUATE

        self._state_graph.add_conditional_edges(
            GraphNodeNames.GENERATE, after_generate_edge, [END, GraphNodeNames.EVALUATE]
        )
        self._state_graph.add_conditional_edges(GraphNodeNames.EVALUATE, evaluate_edge, [END])
        self._state_graph.add_edge(GraphNodeNames.ERROR_NODE, END)
        # END wiring complete
