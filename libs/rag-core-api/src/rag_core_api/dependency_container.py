import qdrant_client
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Selector, Singleton, List  # noqa: WOT001
from langchain_community.document_compressors.flashrank_rerank import FlashrankRerank
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama, VLLMOpenAI
from langchain_qdrant import Qdrant
from langfuse import Langfuse
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from rag_core_api.impl.api_endpoints.default_chat import DefaultChat
from rag_core_api.impl.settings.chat_history_settings import ChatHistorySettings
from rag_core_lib.impl.data_types.content_type import ContentType
from rag_core_lib.impl.langfuse_manager.langfuse_manager import LangfuseManager
from rag_core_lib.impl.llms.llm_factory import llm_provider
from rag_core_lib.impl.llms.llm_type import LLMType
from rag_core_lib.impl.llms.secured_llm import SecuredLLM
from rag_core_lib.impl.secret_provider.no_secret_provider import NoSecretProvider
from rag_core_lib.impl.secret_provider.static_secret_provider_alephalpha import StaticSecretProviderAlephAlpha
from rag_core_lib.impl.secret_provider.static_secret_provider_stackit import StaticSecretProviderStackit
from rag_core_lib.impl.settings.aleph_alpha_settings import AlephAlphaSettings
from rag_core_lib.impl.settings.langfuse_settings import LangfuseSettings
from rag_core_lib.impl.settings.ollama_llm_settings import OllamaSettings
from rag_core_lib.impl.settings.public_aleph_alpha_settings import PublicAlephAlphaSettings
from rag_core_lib.impl.settings.rag_class_types_settings import RAGClassTypeSettings
from rag_core_lib.impl.settings.stackit_vllm_settings import StackitVllmSettings
from rag_core_lib.impl.tracers.langfuse_traced_chain import LangfuseTracedGraph
from rag_core_lib.impl.utils.async_threadsafe_semaphore import AsyncThreadsafeSemaphore

from rag_core_api.impl.answer_generation_chains.answer_generation_chain import AnswerGenerationChain
from rag_core_api.impl.graph.chat_graph import DefaultChatGraph
from rag_core_api.impl.api_endpoints.default_information_pieces_remover import DefaultInformationPiecesRemover
from rag_core_api.impl.api_endpoints.default_information_pieces_uploader import DefaultInformationPiecesUploader
from rag_core_api.impl.embeddings.alephalpha_embedder import AlephAlphaEmbedder
from rag_core_api.impl.embeddings.langchain_community_embedder import LangchainCommunityEmbedder
from rag_core_api.impl.evaluator.langfuse_ragas_evaluator import LangfuseRagasEvaluator
from rag_core_api.impl.mapper.information_piece_mapper import InformationPieceMapper
from rag_core_api.impl.prompt_templates.answer_generation_prompt import ANSWER_GENERATION_PROMPT
from rag_core_api.impl.prompt_templates.question_rephrasing_prompt import QUESTION_REPHRASING_PROMPT
from rag_core_api.impl.reranking.flashrank_reranker import FlashrankReranker
from rag_core_api.impl.retriever.composite_retriever import CompositeRetriever
from rag_core_api.impl.retriever.retriever_quark import RetrieverQuark
from rag_core_api.impl.settings.embedder_class_type_settings import EmbedderClassTypeSettings
from rag_core_api.impl.settings.error_messages import ErrorMessages
from rag_core_api.impl.settings.ragas_settings import RagasSettings
from rag_core_api.impl.settings.reranker_settings import RerankerSettings
from rag_core_api.impl.settings.retriever_settings import RetrieverSettings
from rag_core_api.impl.settings.vector_db_settings import VectorDatabaseSettings
from rag_core_api.impl.vector_databases.qdrant_database import QdrantDatabase
from rag_core_api.impl.embeddings.stackit_embedder import StackitEmbedder
from rag_core_api.impl.settings.stackit_embedder_settings import StackitEmbedderSettings
from rag_core_api.impl.answer_generation_chains.rephrasing_chain import RephrasingChain


class DependencyContainer(DeclarativeContainer):
    """
    Dependency injection container for managing application dependencies.
    """

    class_selector_config = Configuration()
    chat_history_config = Configuration()

    # Settings
    vector_database_settings = VectorDatabaseSettings()
    retriever_settings = RetrieverSettings()
    aleph_alpha_settings = AlephAlphaSettings()
    ollama_settings = OllamaSettings()
    langfuse_settings = LangfuseSettings()
    stackit_vllm_settings = StackitVllmSettings()
    error_messages = ErrorMessages()
    public_aleph_alpha_settings = PublicAlephAlphaSettings()
    rag_class_type_settings = RAGClassTypeSettings()
    ragas_settings = RagasSettings()
    reranker_settings = RerankerSettings()
    embedder_class_type_settings = EmbedderClassTypeSettings()
    stackit_embedder_settings = StackitEmbedderSettings()
    chat_history_settings = ChatHistorySettings()
    chat_history_config.from_dict(chat_history_settings.model_dump())

    class_selector_config.from_dict(rag_class_type_settings.model_dump() | embedder_class_type_settings.model_dump())

    if rag_class_type_settings.llm_type.value == LLMType.ALEPHALPHA.value:
        aleph_alpha_settings.host = public_aleph_alpha_settings.host

    llm_secret_provider = Selector(
        class_selector_config.llm_type,
        alephalpha=Singleton(StaticSecretProviderAlephAlpha, aleph_alpha_settings),
        ollama=Singleton(NoSecretProvider),
        stackit=Singleton(StaticSecretProviderStackit, stackit_vllm_settings),
    )

    embedder = Selector(
        class_selector_config.embedder_type,
        alephalpha=Singleton(
            AlephAlphaEmbedder, aleph_alpha_settings, Singleton(StaticSecretProviderAlephAlpha, aleph_alpha_settings)
        ),
        ollama=Singleton(
            LangchainCommunityEmbedder, embedder=Singleton(OllamaEmbeddings, **ollama_settings.model_dump())
        ),
        stackit=Singleton(StackitEmbedder, stackit_embedder_settings),
    )

    vectordb_client = Singleton(
        qdrant_client.QdrantClient,
        url=vector_database_settings.url,
    )
    vectorstore = Singleton(
        Qdrant,
        client=vectordb_client,
        collection_name=vector_database_settings.collection_name,
        embeddings=embedder,
    )

    vector_database = Singleton(
        QdrantDatabase,
        settings=vector_database_settings,
        embedder=embedder,
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
        alephalpha=Singleton(
            SecuredLLM, llm=Singleton(llm_provider, aleph_alpha_settings), secret_provider=llm_secret_provider
        ),
        ollama=Singleton(llm_provider, ollama_settings, Ollama),
        stackit=Singleton(
            SecuredLLM,
            llm=Singleton(llm_provider, stackit_vllm_settings, VLLMOpenAI),
            secret_provider=llm_secret_provider,
        ),
    )

    prompt = ANSWER_GENERATION_PROMPT
    rephrasing_prompt = QUESTION_REPHRASING_PROMPT

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

    chat_graph = Singleton(
        DefaultChatGraph,
        composed_retriever=composed_retriever,
        rephrasing_chain=rephrasing_chain,
        mapper=information_piece_mapper,
        answer_generation_chain=answer_generation_chain,
        error_messages=error_messages,
        chat_history_settings=chat_history_settings,
    )

    # wrap graph in tracer
    traced_chat_graph = Singleton(
        LangfuseTracedGraph,
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
                api_key=stackit_vllm_settings.api_key,
            ),
            ollama=Singleton(
                ChatOllama,
                model=ragas_settings.model if ragas_settings.model else ollama_settings.model,
                base_url=ollama_settings.base_url,
            ),
            alephalpha=Singleton(
                lambda: exec(  # noqa: S102
                    'raise NotImplementedError("Alephalpha is currently not supported for evaluation")'
                )
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
