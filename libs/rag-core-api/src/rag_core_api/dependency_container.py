import qdrant_client
from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Configuration, Selector, Singleton, List  # noqa: WOT001
from langchain_community.document_compressors.flashrank_rerank import FlashrankRerank
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama, VLLMOpenAI
from langchain_qdrant import Qdrant
from langfuse import Langfuse

from rag_core_api.impl.settings.chat_history_settings import ChatHistorySettings
from rag_core_lib.impl.data_types.content_type import ContentType
from rag_core_lib.impl.langfuse_manager.langfuse_manager import LangfuseManager
from rag_core_lib.impl.llms.llm_factory import llm_provider
from rag_core_lib.impl.llms.llm_type import LLMType
from rag_core_lib.impl.llms.secured_llm import SecuredLLM
from rag_core_lib.impl.secret_provider.dynamic_secret_provider import DynamicSecretProvider
from rag_core_lib.impl.secret_provider.no_secret_provider import NoSecretProvider
from rag_core_lib.impl.secret_provider.static_secret_provider_alephalpha import StaticSecretProviderAlephAlpha
from rag_core_lib.impl.secret_provider.static_secret_provider_stackit import StaticSecretProviderStackit
from rag_core_lib.impl.settings.aleph_alpha_settings import AlephAlphaSettings
from rag_core_lib.impl.settings.langfuse_settings import LangfuseSettings
from rag_core_lib.impl.settings.ollama_llm_settings import OllamaSettings
from rag_core_lib.impl.settings.public_aleph_alpha_settings import PublicAlephAlphaSettings
from rag_core_lib.impl.settings.rag_class_types_settings import RAGClassTypeSettings
from rag_core_lib.impl.settings.stackit_myapi_llm_settings import StackitMyAPILLMSettings
from rag_core_lib.impl.settings.stackit_vllm_settings import StackitVllmSettings
from rag_core_lib.impl.tracers.langfuse_traced_chain import LangfuseTracedChain

from rag_core_api.impl import rag_api
from rag_core_api.impl.answer_generation_chains.answer_generation_chain import AnswerGenerationChain
from rag_core_api.impl.api_endpoints.default_chat_graph import DefaultChatGraph
from rag_core_api.impl.api_endpoints.default_searcher import DefaultSearcher
from rag_core_api.impl.api_endpoints.default_source_documents_remover import DefaultSourceDocumentsRemover
from rag_core_api.impl.api_endpoints.default_source_documents_uploader import DefaultSourceDocumentsUploader
from rag_core_api.impl.embeddings.alephalpha_embedder import AlephAlphaEmbedder
from rag_core_api.impl.embeddings.langchain_community_embedder import LangchainCommunityEmbedder
from rag_core_api.impl.evaluator.langfuse_ragas_evaluator import LangfuseRagasEvaluator
from rag_core_api.impl.mapper.source_document_mapper import SourceDocumentMapper
from rag_core_api.impl.prompt_templates.answer_generation_prompt import ANSWER_GENERATION_PROMPT
from rag_core_api.impl.prompt_templates.answer_rephrasing_prompt import ANSWER_REPHRASING_PROMPT
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

    wiring_config = WiringConfiguration(modules=[rag_api])

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
    stackit_myapi_llm_settings = StackitMyAPILLMSettings()
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
        myapi=Singleton(DynamicSecretProvider, stackit_myapi_llm_settings),
        alephalpha=Singleton(StaticSecretProviderAlephAlpha, aleph_alpha_settings),
        ollama=Singleton(NoSecretProvider),
        stackit=Singleton(StaticSecretProviderStackit, stackit_vllm_settings),
    )

    embedder = Selector(
        class_selector_config.embedder_type,
        myapi=Singleton(
            AlephAlphaEmbedder, aleph_alpha_settings, Singleton(DynamicSecretProvider, stackit_myapi_llm_settings)
        ),
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

    source_documents_uploader = Singleton(DefaultSourceDocumentsUploader, vector_database)

    source_documents_remover = Singleton(DefaultSourceDocumentsRemover, vector_database)

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

    source_document_mapper = Singleton(SourceDocumentMapper)

    searcher = Singleton(DefaultSearcher, composed_retriever, source_document_mapper, error_messages)

    large_language_model = Selector(
        class_selector_config.llm_type,
        myapi=Singleton(
            SecuredLLM, llm=Singleton(llm_provider, aleph_alpha_settings), secret_provider=llm_secret_provider
        ),
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
    rephrasing_prompt = ANSWER_REPHRASING_PROMPT

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
        searcher=searcher,
        rephrasing_chain=rephrasing_chain,
        mapper=source_document_mapper,
        answer_generation_chain=answer_generation_chain,
        error_messages=error_messages,
    )

    # wrap graph in tracer
    traced_chat_graph = Singleton(
        LangfuseTracedChain,
        inner_chain=chat_graph,
        settings=langfuse_settings,
    )

    evaluator = Singleton(
        LangfuseRagasEvaluator,
        chat_chain=traced_chat_graph,
        settings=ragas_settings,
        langfuse_manager=langfuse_manager,
        embedder=embedder,
    )
