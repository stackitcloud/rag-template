import qdrant_client
from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Configuration, List, Selector, Singleton
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_qdrant import Qdrant
from langchain.retrievers.document_compressors.flashrank_rerank import FlashrankRerank
from rag_core_api.impl.reranking.flashrank_reranker import FlashrankReranker
from rag_core_api.impl.settings.reranker_settings import RerankerSettings
from rag_core_api.impl.embeddings.alephalpha_embedder import AlephAlphaEmbedder
from rag_core_lib.impl.data_types.content_type import ContentType
from rag_core_lib.impl.llms.llm_factory import llm_provider
from rag_core_lib.impl.llms.llm_type import LLMType
from rag_core_lib.impl.llms.secured_llm import SecuredLLM
from rag_core_lib.impl.secret_provider.dynamic_secret_provider import (
    DynamicSecretProvider,
)
from rag_core_lib.impl.secret_provider.no_secret_provider import NoSecretProvider
from rag_core_lib.impl.secret_provider.static_secret_provider import (
    StaticSecretProvider,
)
from rag_core_lib.impl.settings.aleph_alpha_settings import AlephAlphaSettings
from rag_core_lib.impl.settings.langfuse_settings import LangfuseSettings
from rag_core_lib.impl.settings.ollama_llm_settings import OllamaSettings
from rag_core_lib.impl.settings.public_aleph_alpha_settings import (
    PublicAlephAlphaSettings,
)
from rag_core_lib.impl.settings.rag_class_types_settings import RAGClassTypeSettings
from rag_core_lib.impl.settings.stackit_myapi_llm_settings import (
    StackitMyAPILLMSettings,
)
from rag_core_lib.impl.tracers.langfuse_traced_chain import LangfuseTracedChain

from rag_core_api.impl import rag_api
from rag_core_api.impl.mapper.source_document_mapper import SourceDocumentMapper
from rag_core_api.impl.answer_generation_chains.answer_generation_chain import (
    AnswerGenerationChain,
)
from rag_core_api.impl.api_endpoints.default_chat_chain import DefaultChatChain
from rag_core_api.impl.api_endpoints.default_searcher import DefaultSearcher
from rag_core_api.impl.api_endpoints.default_source_documents_remover import (
    DefaultSourceDocumentsRemover,
)
from rag_core_api.impl.api_endpoints.default_source_documents_uploader import (
    DefaultSourceDocumentsUploader,
)
from rag_core_api.impl.embeddings.langchain_community_embedder import (
    LangchainCommunityEmbedder,
)
from rag_core_api.impl.prompt_templates.answer_generation_prompt import (
    ANSWER_GENERATION_PROMPT,
)
from rag_core_api.impl.retriever.composite_retriever import CompositeRetriever
from rag_core_api.impl.retriever.retriever_quark import RetrieverQuark
from rag_core_api.impl.settings.error_messages import ErrorMessages
from rag_core_api.impl.settings.retriever_settings import RetrieverSettings
from rag_core_api.impl.settings.vector_db_settings import VectorDatabaseSettings
from rag_core_api.impl.vector_databases.qdrant_database import QdrantDatabase
from rag_core_api.impl.settings.embedder_class_type_settings import EmbedderClassTypeSettings


class DependencyContainer(DeclarativeContainer):
    """
    Dependency injection container for managing application dependencies.
    """

    wiring_config = WiringConfiguration(modules=[rag_api])

    class_selector_config = Configuration()

    # Settings
    vector_database_settings = VectorDatabaseSettings()
    retriever_settings = RetrieverSettings()
    aleph_alpha_settings = AlephAlphaSettings()
    ollama_settings = OllamaSettings()
    langfuse_settings = LangfuseSettings()
    error_messages = ErrorMessages()
    stackit_myapi_llm_settings = StackitMyAPILLMSettings()
    public_aleph_alpha_settings = PublicAlephAlphaSettings()
    rag_class_type_settings = RAGClassTypeSettings()
    reranker_settings = RerankerSettings()
    embedder_class_type_settings = EmbedderClassTypeSettings()

    class_selector_config.from_dict(rag_class_type_settings.model_dump() | embedder_class_type_settings.model_dump())

    if rag_class_type_settings.llm_type.value == LLMType.ALEPHALPHA.value:
        aleph_alpha_settings.host = public_aleph_alpha_settings.host

    llm_secret_provider = Selector(
        class_selector_config.llm_type,
        myapi=Singleton(DynamicSecretProvider, stackit_myapi_llm_settings),
        alephalpha=Singleton(StaticSecretProvider, aleph_alpha_settings),
        ollama=Singleton(NoSecretProvider),
    )

    embedder = Selector(
        class_selector_config.embedder_type,
        myapi=Singleton(AlephAlphaEmbedder, aleph_alpha_settings, llm_secret_provider),
        alephalpha=Singleton(AlephAlphaEmbedder, aleph_alpha_settings, llm_secret_provider),
        ollama=Singleton(
            LangchainCommunityEmbedder, embedder=Singleton(OllamaEmbeddings, **ollama_settings.model_dump())
        ),
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
        myapi=Singleton(llm_provider, aleph_alpha_settings),
        alephalpha=Singleton(llm_provider, aleph_alpha_settings),
        ollama=Singleton(llm_provider, ollama_settings, Ollama),
    )

    # Add secret provider to model
    large_language_model = Selector(
        class_selector_config.llm_type,
        myapi=Singleton(SecuredLLM, llm=large_language_model, secret_provider=llm_secret_provider),
        alephalpha=Singleton(SecuredLLM, llm=aleph_alpha_settings, secret_provider=llm_secret_provider),
        ollama=large_language_model,
    )

    prompt = ANSWER_GENERATION_PROMPT

    answer_generation_chain = Singleton(
        AnswerGenerationChain,
        llm=large_language_model,
        prompt=prompt,
    )

    chat_chain = Singleton(
        DefaultChatChain,
        composed_retriever=composed_retriever,
        searcher=searcher,
        mapper=source_document_mapper,
        answer_generation_chain=answer_generation_chain,
        error_messages=error_messages,
    )

    # wrap chain in tracer
    traced_chat_chain = Singleton(
        LangfuseTracedChain,
        inner_chain=chat_chain,
        settings=langfuse_settings,
    )
