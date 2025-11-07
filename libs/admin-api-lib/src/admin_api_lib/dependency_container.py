"""Module for the DependencyContainer class."""

from admin_api_lib.impl.api_endpoints.default_file_uploader import DefaultFileUploader
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, List, Selector, Singleton
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langfuse import Langfuse

from admin_api_lib.extractor_api_client.openapi_client.api.extractor_api import (
    ExtractorApi,
)
from admin_api_lib.extractor_api_client.openapi_client.api_client import ApiClient
from admin_api_lib.extractor_api_client.openapi_client.configuration import (
    Configuration as ExtractorConfiguration,
)
from admin_api_lib.impl.api_endpoints.default_source_uploader import DefaultSourceUploader
from admin_api_lib.impl.api_endpoints.default_document_deleter import (
    DefaultDocumentDeleter,
)
from admin_api_lib.impl.api_endpoints.default_document_reference_retriever import (
    DefaultDocumentReferenceRetriever,
)

from admin_api_lib.impl.api_endpoints.default_documents_status_retriever import (
    DefaultDocumentsStatusRetriever,
)
from admin_api_lib.impl.chunker.semantic_text_chunker import SemanticTextChunker
from admin_api_lib.impl.chunker.text_chunker import TextChunker
from admin_api_lib.impl.file_services.s3_service import S3Service
from admin_api_lib.impl.information_enhancer.general_enhancer import GeneralEnhancer
from admin_api_lib.impl.information_enhancer.page_summary_enhancer import (
    PageSummaryEnhancer,
)
from admin_api_lib.impl.key_db.file_status_key_value_store import (
    FileStatusKeyValueStore,
)
from admin_api_lib.impl.mapper.informationpiece2document import (
    InformationPiece2Document,
)
from admin_api_lib.impl.settings.chunker_class_type_settings import ChunkerClassTypeSettings
from admin_api_lib.impl.settings.chunker_settings import ChunkerSettings
from admin_api_lib.impl.settings.document_extractor_settings import (
    DocumentExtractorSettings,
)
from admin_api_lib.impl.settings.key_value_settings import KeyValueSettings
from admin_api_lib.impl.settings.rag_api_settings import RAGAPISettings
from admin_api_lib.impl.settings.s3_settings import S3Settings
from admin_api_lib.impl.settings.source_uploader_settings import SourceUploaderSettings
from admin_api_lib.impl.settings.summarizer_settings import SummarizerSettings
from admin_api_lib.impl.summarizer.langchain_summarizer import LangchainSummarizer
from admin_api_lib.prompt_templates.summarize_prompt import SUMMARIZE_PROMPT
from admin_api_lib.rag_backend_client.openapi_client.api.rag_api import RagApi
from admin_api_lib.rag_backend_client.openapi_client.api_client import (
    ApiClient as RagApiClient,
)
from admin_api_lib.rag_backend_client.openapi_client.configuration import (
    Configuration as RagConfiguration,
)
from rag_core_lib.impl.embeddings.langchain_community_embedder import (
    LangchainCommunityEmbedder,
)
from rag_core_lib.impl.embeddings.stackit_embedder import StackitEmbedder
from rag_core_lib.impl.langfuse_manager.langfuse_manager import LangfuseManager
from rag_core_lib.impl.llms.llm_factory import chat_model_provider
from rag_core_lib.impl.settings.embedder_class_type_settings import (
    EmbedderClassTypeSettings,
)
from rag_core_lib.impl.settings.langfuse_settings import LangfuseSettings
from rag_core_lib.impl.settings.ollama_embedder_settings import OllamaEmbedderSettings
from rag_core_lib.impl.settings.ollama_llm_settings import OllamaSettings
from rag_core_lib.impl.settings.rag_class_types_settings import RAGClassTypeSettings
from rag_core_lib.impl.settings.retry_decorator_settings import RetryDecoratorSettings
from rag_core_lib.impl.settings.stackit_embedder_settings import StackitEmbedderSettings
from rag_core_lib.impl.settings.stackit_vllm_settings import StackitVllmSettings
from rag_core_lib.impl.tracers.langfuse_traced_runnable import LangfuseTracedRunnable
from rag_core_lib.impl.utils.async_threadsafe_semaphore import AsyncThreadsafeSemaphore


class DependencyContainer(DeclarativeContainer):
    """Dependency injection container for managing application dependencies."""

    class_selector_config = Configuration()
    chunker_selector_config = Configuration()

    # Settings
    s3_settings = S3Settings()
    chunker_settings = ChunkerSettings()
    chunker_embedder_type_settings = EmbedderClassTypeSettings()
    stackit_chunker_embedder_settings = StackitEmbedderSettings()
    ollama_chunker_embedder_settings = OllamaEmbedderSettings()
    ollama_settings = OllamaSettings()
    langfuse_settings = LangfuseSettings()
    stackit_vllm_settings = StackitVllmSettings()
    document_extractor_settings = DocumentExtractorSettings()
    rag_class_type_settings = RAGClassTypeSettings()
    rag_api_settings = RAGAPISettings()
    key_value_store_settings = KeyValueSettings()
    summarizer_settings = SummarizerSettings()
    source_uploader_settings = SourceUploaderSettings()
    retry_decorator_settings = RetryDecoratorSettings()
    chunker_type_settings = ChunkerClassTypeSettings()

    class_selector_config.from_dict(rag_class_type_settings.model_dump() | chunker_embedder_type_settings.model_dump())
    chunker_selector_config.from_dict(chunker_type_settings.model_dump())

    key_value_store = Singleton(FileStatusKeyValueStore, key_value_store_settings)
    file_service = Singleton(S3Service, s3_settings=s3_settings)

    text_splitter = Singleton(RecursiveCharacterTextSplitter)(
        chunk_size=chunker_settings.max_size, chunk_overlap=chunker_settings.overlap
    )

    semantic_chunker_embeddings = Selector(
        class_selector_config.embedder_type,
        stackit=Singleton(
            StackitEmbedder,
            stackit_chunker_embedder_settings,
            retry_decorator_settings,
        ),
        ollama=Singleton(
            LangchainCommunityEmbedder,
            embedder=Singleton(
                OllamaEmbeddings,
                model=ollama_chunker_embedder_settings.model,
                base_url=ollama_chunker_embedder_settings.base_url,
            ),
        ),
    )

    semantic_chunker = Singleton(
        SemanticTextChunker,
        embeddings=semantic_chunker_embeddings,
        breakpoint_threshold_type=chunker_settings.breakpoint_threshold_type,
        breakpoint_threshold_amount=chunker_settings.breakpoint_threshold_amount,
        buffer_size=chunker_settings.buffer_size,
        min_chunk_size=chunker_settings.min_size,
        max_chunk_size=chunker_settings.max_size,
        recursive_text_splitter=text_splitter,
        overlap=chunker_settings.overlap,
    )

    chunker = Selector(
        chunker_selector_config.chunker_type,
        recursive=Singleton(TextChunker, text_splitter),
        semantic=semantic_chunker,
    )
    extractor_api_configuration = Singleton(ExtractorConfiguration, host=document_extractor_settings.host)
    document_extractor_api_client = Singleton(ApiClient, extractor_api_configuration)
    document_extractor = Singleton(ExtractorApi, document_extractor_api_client)

    rag_api_configuration = Singleton(RagConfiguration, host=rag_api_settings.host)
    rag_api_client = Singleton(RagApiClient, configuration=rag_api_configuration)
    rag_api = Singleton(RagApi, rag_api_client)

    information_mapper = Singleton(InformationPiece2Document)

    large_language_model = Selector(
        class_selector_config.llm_type,
        ollama=Singleton(chat_model_provider, ollama_settings, "ollama"),
        stackit=Singleton(chat_model_provider, stackit_vllm_settings, "openai"),
    )

    summary_text_splitter = Singleton(RecursiveCharacterTextSplitter)(
        chunk_size=summarizer_settings.maximum_input_size, chunk_overlap=chunker_settings.overlap
    )

    langfuse = Singleton(
        Langfuse,
        public_key=langfuse_settings.public_key,
        secret_key=langfuse_settings.secret_key,
        host=langfuse_settings.host,
    )
    summarizer_prompt = SUMMARIZE_PROMPT

    langfuse_manager = Singleton(
        LangfuseManager,
        langfuse=langfuse,
        managed_prompts={
            LangchainSummarizer.__name__: summarizer_prompt,
        },
        llm=large_language_model,
    )

    summarizer = Singleton(
        LangchainSummarizer,
        langfuse_manager=langfuse_manager,
        chunker=summary_text_splitter,
        semaphore=Singleton(AsyncThreadsafeSemaphore, summarizer_settings.maximum_concurrency),
        summarizer_settings=summarizer_settings,
        retry_decorator_settings=retry_decorator_settings,
    )

    summary_enhancer = List(
        Singleton(PageSummaryEnhancer, summarizer, chunker_settings),
    )
    untraced_information_enhancer = Singleton(
        GeneralEnhancer,
        summary_enhancer,
    )
    information_enhancer = Singleton(
        LangfuseTracedRunnable,
        inner_chain=untraced_information_enhancer,
        settings=langfuse_settings,
    )

    document_deleter = Singleton(
        DefaultDocumentDeleter, rag_api=rag_api, file_service=file_service, key_value_store=key_value_store
    )
    documents_status_retriever = Singleton(DefaultDocumentsStatusRetriever, key_value_store=key_value_store)

    document_reference_retriever = Singleton(DefaultDocumentReferenceRetriever, file_service=file_service)

    source_uploader = Singleton(
        DefaultSourceUploader,
        extractor_api=document_extractor,
        rag_api=rag_api,
        information_enhancer=information_enhancer,
        information_mapper=information_mapper,
        chunker=chunker,
        key_value_store=key_value_store,
        document_deleter=document_deleter,
        settings=source_uploader_settings,
    )

    file_uploader = Singleton(
        DefaultFileUploader,
        extractor_api=document_extractor,
        rag_api=rag_api,
        information_enhancer=information_enhancer,
        information_mapper=information_mapper,
        chunker=chunker,
        key_value_store=key_value_store,
        document_deleter=document_deleter,
        file_service=file_service,
    )
