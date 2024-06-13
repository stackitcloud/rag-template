from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Singleton, Selector, Configuration, List
from rag_core.impl.answer_generation_chains.answer_generation_chain import AnswerGenerationChain
from rag_core.impl.data_types.content_type import ContentType
from rag_core.impl.llms.llm_factory import llm_provider
from rag_core.impl.llms.llm_type import LLMType
from rag_core.impl.llms.secured_llm import SecuredLLM
from rag_core.impl.prompt_templates.answer_generation_prompt import ANSWER_GENERATION_PROMPT
from rag_core.impl.embeddings.alephalpha_embedder import AlephAlphaEmbedder
from rag_core.impl.retriever.composite_retriever import CompositeRetriever
from rag_core.impl.retriever.retriever_quark import RetrieverQuark
from rag_core.impl.secret_provider.dynamic_secret_provider import DynamicSecretProvider
from rag_core.impl.secret_provider.no_secret_provider import NoSecretProvider
from rag_core.impl.secret_provider.static_secret_provider import StaticSecretProvider
from rag_core.impl.settings.aleph_alpha_settings import AlephAlphaSettings
from rag_core.impl.settings.error_messages import ErrorMessages
from rag_core.impl.settings.langfuse_settings import LangfuseSettings
from rag_core.impl.settings.ollama_llm_settings import OllamaSettings
from rag_core.impl.settings.public_aleph_alpha_settings import PublicAlephAlphaSettings
from rag_core.impl.settings.rag_class_types_settings import RAGClassTypeSettings
from rag_core.impl.settings.retriever_settings import RetrieverSettings
from rag_core.impl.settings.stackit_myapi_llm_settings import StackitMyAPILLMSettings
import qdrant_client
from langchain_qdrant import Qdrant
from langchain_community.llms import Ollama
from rag_core.impl.settings.vector_db_settings import VectorDatabaseSettings
from rag_core.impl.tracers.langfuse_traced_chain import LangfuseTracedChain
from rag_core.impl.vector_databases.qdrant_database import QdrantDatabase


class Container(DeclarativeContainer):
    """
    Dependency injection container for managing application dependencies.
    """

    wiring_config = WiringConfiguration(modules=["rag_core.impl.rag_api"])

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

    class_selector_config.from_dict(rag_class_type_settings.model_dump())

    if rag_class_type_settings.llm_type.value == LLMType.ALEPHALPHA.value:
        aleph_alpha_settings.host = public_aleph_alpha_settings.host

    llm_secret_provider = Selector(
        class_selector_config.llm_type,
        myapi=Singleton(DynamicSecretProvider, stackit_myapi_llm_settings),
        alephalpha=Singleton(StaticSecretProvider, aleph_alpha_settings),
        ollama=Singleton(NoSecretProvider),
    )

    embedder_secret_provider = Selector(
        class_selector_config.llm_type,
        myapi=Singleton(DynamicSecretProvider, stackit_myapi_llm_settings),
        alephalpha=Singleton(StaticSecretProvider, aleph_alpha_settings),
        ollama=Singleton(
            DynamicSecretProvider, stackit_myapi_llm_settings
        ),  # TODO: We should make a setting for the embedder type
    )

    prompt = ANSWER_GENERATION_PROMPT

    embedder = Singleton(
        AlephAlphaEmbedder,
        settings=aleph_alpha_settings,
        secret_provider=embedder_secret_provider,
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
        CompositeRetriever, List(image_retriever, table_retriever, text_retriever, summary_retriever)
    )

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

    answer_generation_chain = Singleton(
        AnswerGenerationChain,
        llm=large_language_model,
        prompt=prompt,
    )

    # wrap chain in tracer
    answer_generation_chain = Singleton(
        LangfuseTracedChain,
        inner_chain=answer_generation_chain,
        settings=LangfuseSettings,
    )
