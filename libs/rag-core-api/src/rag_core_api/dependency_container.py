"""Module containing the dependency injection container for managing application dependencies."""

import qdrant_client
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (  # noqa: WOT001
    Configuration,
    List,
    Selector,
    Singleton,
)
from langchain_community.document_compressors.flashrank_rerank import FlashrankRerank
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_qdrant import QdrantVectorStore, FastEmbedSparse
from langfuse import Langfuse

from rag_core_api.impl.answer_generation_chains.answer_generation_chain import (
    AnswerGenerationChain,
)
from rag_core_api.impl.answer_generation_chains.rephrasing_chain import RephrasingChain
from rag_core_api.impl.answer_generation_chains.language_detection_chain import LanguageDetectionChain
from rag_core_api.impl.api_endpoints.default_chat import DefaultChat
from rag_core_api.impl.api_endpoints.default_information_pieces_remover import (
    DefaultInformationPiecesRemover,
)
from rag_core_api.impl.api_endpoints.default_information_pieces_uploader import (
    DefaultInformationPiecesUploader,
)
from rag_core_api.impl.embeddings.langchain_community_embedder import (
    LangchainCommunityEmbedder,
)


from rag_core_api.impl.embeddings.stackit_embedder import StackitEmbedder
from rag_core_api.impl.evaluator.langfuse_ragas_evaluator import LangfuseRagasEvaluator
from rag_core_api.impl.graph.chat_graph import DefaultChatGraph
from rag_core_api.impl.reranking.flashrank_reranker import FlashrankReranker
from rag_core_api.impl.retriever.composite_retriever import CompositeRetriever
from rag_core_api.impl.retriever.retriever_quark import RetrieverQuark
from rag_core_api.impl.settings.chat_history_settings import ChatHistorySettings
from rag_core_api.impl.settings.embedder_class_type_settings import (
    EmbedderClassTypeSettings,
)
from rag_core_api.impl.settings.error_messages import ErrorMessages
from rag_core_api.impl.settings.ollama_embedder_settings import OllamaEmbedderSettings
from rag_core_api.impl.settings.ragas_settings import RagasSettings
from rag_core_api.impl.settings.reranker_settings import RerankerSettings
from rag_core_api.impl.settings.retriever_settings import RetrieverSettings
from rag_core_api.impl.settings.sparse_embedder_settings import SparseEmbedderSettings
from rag_core_api.impl.settings.stackit_embedder_settings import StackitEmbedderSettings
from rag_core_api.impl.settings.vector_db_settings import VectorDatabaseSettings
from rag_core_api.impl.vector_databases.qdrant_database import QdrantDatabase
from rag_core_api.mapper.information_piece_mapper import InformationPieceMapper
from rag_core_api.prompt_templates.answer_generation_prompt import (
    ANSWER_GENERATION_PROMPT,
)
from rag_core_api.prompt_templates.question_rephrasing_prompt import (
    QUESTION_REPHRASING_PROMPT,
)
from rag_core_api.prompt_templates.language_detection_prompt import LANGUAGE_DETECTION_PROMPT
from rag_core_lib.impl.data_types.content_type import ContentType
from rag_core_lib.impl.langfuse_manager.langfuse_manager import LangfuseManager
from rag_core_lib.impl.llms.llm_factory import chat_model_provider
from rag_core_lib.impl.settings.langfuse_settings import LangfuseSettings
from rag_core_lib.impl.settings.ollama_llm_settings import OllamaSettings
from rag_core_lib.impl.settings.rag_class_types_settings import RAGClassTypeSettings
from rag_core_lib.impl.settings.retry_decorator_settings import RetryDecoratorSettings
from rag_core_lib.impl.settings.stackit_vllm_settings import StackitVllmSettings
from rag_core_lib.impl.tracers.langfuse_traced_runnable import LangfuseTracedRunnable
from rag_core_lib.impl.utils.async_threadsafe_semaphore import AsyncThreadsafeSemaphore


class DependencyContainer(DeclarativeContainer):
    """Dependency injection container for managing application dependencies."""

    class_selector_config = Configuration()
    chat_history_config = Configuration()

    # Settings
    vector_database_settings = VectorDatabaseSettings()
    retriever_settings = RetrieverSettings()
    ollama_settings = OllamaSettings()
    ollama_embedder_settings = OllamaEmbedderSettings()
    langfuse_settings = LangfuseSettings()
    stackit_vllm_settings = StackitVllmSettings()
    error_messages = ErrorMessages()
    rag_class_type_settings = RAGClassTypeSettings()
    ragas_settings = RagasSettings()
    reranker_settings = RerankerSettings()
    embedder_class_type_settings = EmbedderClassTypeSettings()
    stackit_embedder_settings = StackitEmbedderSettings()
    chat_history_settings = ChatHistorySettings()
    sparse_embedder_settings = SparseEmbedderSettings()
    retry_decorator_settings = RetryDecoratorSettings()
    chat_history_config.from_dict(chat_history_settings.model_dump())

    class_selector_config.from_dict(rag_class_type_settings.model_dump() | embedder_class_type_settings.model_dump())

    embedder = Selector(
        class_selector_config.embedder_type,
        ollama=Singleton(
            LangchainCommunityEmbedder, embedder=Singleton(OllamaEmbeddings, **ollama_embedder_settings.model_dump())
        ),
        stackit=Singleton(StackitEmbedder, stackit_embedder_settings, retry_decorator_settings),
    )

    sparse_embedder = Singleton(FastEmbedSparse, **sparse_embedder_settings.model_dump())

    vectordb_client = Singleton(
        qdrant_client.QdrantClient,
        location=vector_database_settings.location,
    )

    vectorstore = Singleton(
        QdrantVectorStore,
        client=vectordb_client,
        collection_name=vector_database_settings.collection_name,
        embedding=embedder,
        sparse_embedding=sparse_embedder,
        validate_collection_config=False,
        retrieval_mode=vector_database_settings.retrieval_mode,
    )

    vector_database = Singleton(
        QdrantDatabase,
        settings=vector_database_settings,
        embedder=embedder,
        sparse_embedder=sparse_embedder,
        vectorstore=vectorstore,
    )

    flashrank_reranker = Singleton(FlashrankRerank, top_n=reranker_settings.k_documents)
    reranker = Singleton(FlashrankReranker, flashrank_reranker)

    information_pieces_uploader = Singleton(DefaultInformationPiecesUploader, vector_database)

    information_pieces_remover = Singleton(DefaultInformationPiecesRemover, vector_database)

    image_retriever = Singleton(
        RetrieverQuark,
        vector_database,
        ContentType.IMAGE,
        retriever_settings.image_k_documents,
        retriever_settings.image_threshold,
    )
    table_retriever = Singleton(
        RetrieverQuark,
        vector_database,
        ContentType.TABLE,
        retriever_settings.table_k_documents,
        retriever_settings.table_threshold,
    )
    text_retriever = Singleton(
        RetrieverQuark,
        vector_database,
        ContentType.TEXT,
        retriever_settings.k_documents,
        retriever_settings.threshold,
    )
    summary_retriever = Singleton(
        RetrieverQuark,
        vector_database,
        ContentType.SUMMARY,
        retriever_settings.summary_k_documents,
        retriever_settings.summary_threshold,
    )

    composed_retriever = Singleton(
        CompositeRetriever,
        List(image_retriever, table_retriever, text_retriever, summary_retriever),
        reranker,
    )

    information_piece_mapper = Singleton(InformationPieceMapper)

    large_language_model = Selector(
        class_selector_config.llm_type,
        ollama=Singleton(chat_model_provider, ollama_settings, "ollama"),
        stackit=Singleton(chat_model_provider, stackit_vllm_settings, "openai"),
    )

    prompt = ANSWER_GENERATION_PROMPT
    rephrasing_prompt = QUESTION_REPHRASING_PROMPT
    language_detection_prompt = LANGUAGE_DETECTION_PROMPT

    langfuse = Singleton(
        Langfuse,
        public_key=langfuse_settings.public_key,
        secret_key=langfuse_settings.secret_key,
        host=langfuse_settings.host,
    )

    langfuse_manager = Singleton(
        LangfuseManager,
        langfuse=langfuse,
        managed_prompts={
            AnswerGenerationChain.__name__: prompt,
            RephrasingChain.__name__: rephrasing_prompt,
            LanguageDetectionChain.__name__: language_detection_prompt,
        },
        llm=large_language_model,
    )

    answer_generation_chain = Singleton(
        AnswerGenerationChain,
        langfuse_manager=langfuse_manager,
    )

    rephrasing_chain = Singleton(
        RephrasingChain,
        langfuse_manager=langfuse_manager,
    )

    language_detection_chain = Singleton(
        LanguageDetectionChain,
        langfuse_manager=langfuse_manager,
    )

    chat_graph = Singleton(
        DefaultChatGraph,
        composed_retriever=composed_retriever,
        rephrasing_chain=rephrasing_chain,
        language_detection_chain=language_detection_chain,
        mapper=information_piece_mapper,
        answer_generation_chain=answer_generation_chain,
        error_messages=error_messages,
        chat_history_settings=chat_history_settings,
    )

    # wrap graph in tracer
    traced_chat_graph = Singleton(
        LangfuseTracedRunnable,
        inner_chain=chat_graph,
        settings=langfuse_settings,
    )

    chat_endpoint = Singleton(DefaultChat, traced_chat_graph)

    ragas_llm = (
        Singleton(
            ChatOpenAI,
            model=ragas_settings.model,
            timeout=ragas_settings.timeout,
            api_key=ragas_settings.openai_api_key,
        )
        if ragas_settings.use_openai
        else Selector(
            class_selector_config.llm_type,
            stackit=Singleton(
                ChatOpenAI,
                model=ragas_settings.model if ragas_settings.model else stackit_vllm_settings.model,
                timeout=ragas_settings.timeout,
                openai_api_base=stackit_vllm_settings.base_url,
                openai_api_key=stackit_vllm_settings.api_key,
            ),
            ollama=Singleton(
                ChatOllama,
                model=ragas_settings.model if ragas_settings.model else ollama_settings.model,
                base_url=ollama_settings.base_url,
            ),
        )
    )

    evaluator = Singleton(
        LangfuseRagasEvaluator,
        chat_endpoint=chat_endpoint,
        settings=ragas_settings,
        langfuse_manager=langfuse_manager,
        embedder=embedder,
        semaphore=Singleton(AsyncThreadsafeSemaphore, ragas_settings.max_concurrency),
        chat_history_config=chat_history_config,
        chat_llm=ragas_llm,
    )
