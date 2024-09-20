from asyncio import Semaphore
from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Configuration, List, Selector, Singleton  # noqa: WOT001
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama, VLLMOpenAI
from langfuse import Langfuse

from rag_core_lib.impl.llms.llm_factory import llm_provider
from rag_core_lib.impl.llms.llm_type import LLMType
from rag_core_lib.impl.llms.secured_llm import SecuredLLM
from rag_core_lib.impl.langfuse_manager.langfuse_manager import LangfuseManager
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

from admin_backend.document_extractor_client.openapi_client.api.extractor_api import ExtractorApi
from admin_backend.document_extractor_client.openapi_client.api_client import ApiClient
from admin_backend.document_extractor_client.openapi_client.configuration import Configuration as ExtractorConfiguration
from admin_backend.impl import admin_api
from admin_backend.impl.chunker.text_chunker import TextChunker
from admin_backend.impl.file_services.s3_service import S3Service
from admin_backend.impl.information_enhancer.general_enhancer import GeneralEnhancer
from admin_backend.impl.information_enhancer.page_summary_enhancer import PageSummaryEnhancer
from admin_backend.impl.information_enhancer.single_summary_enhancer import SingleSummaryEnhancer
from admin_backend.impl.key_db.file_status_key_value_store import FileStatusKeyValueStore
from admin_backend.impl.mapper.informationpiece2document import InformationPiece2Document
from admin_backend.impl.settings.chunker_settings import ChunkerSettings
from admin_backend.impl.settings.document_extractor_settings import DocumentExtractorSettings
from admin_backend.impl.settings.key_value_settings import KeyValueSettings
from admin_backend.impl.settings.rag_api_settings import RAGAPISettings
from admin_backend.impl.settings.s3_settings import S3Settings
from admin_backend.impl.summarizer.langchain_summarizer import LangchainSummarizer
from admin_backend.rag_backend_client.openapi_client.api.rag_api import RagApi
from admin_backend.rag_backend_client.openapi_client.api_client import ApiClient as RagApiClient
from admin_backend.impl.settings.summarizer_settings import SummarizerSettings
from admin_backend.impl.prompt_templates.summarize_prompt import SUMMARIZE_PROMPT


class DependencyContainer(DeclarativeContainer):
    """
    Dependency injection container for managing application dependencies.
    """

    wiring_config = WiringConfiguration(modules=[admin_api])

    class_selector_config = Configuration()

    # Settings
    s3_settings = S3Settings()
    chunker_settings = ChunkerSettings()
    aleph_alpha_settings = AlephAlphaSettings()
    ollama_settings = OllamaSettings()
    langfuse_settings = LangfuseSettings()
    stackit_myapi_llm_settings = StackitMyAPILLMSettings()
    stackit_vllm_settings = StackitVllmSettings()
    document_extractor_settings = DocumentExtractorSettings()
    public_aleph_alpha_settings = PublicAlephAlphaSettings()
    rag_class_type_settings = RAGClassTypeSettings()
    rag_api_settings = RAGAPISettings()
    key_value_store_settings = KeyValueSettings()
    summarizer_settings = SummarizerSettings()

    if rag_class_type_settings.llm_type == LLMType.ALEPHALPHA.value:
        aleph_alpha_settings.host = public_aleph_alpha_settings.host

    llm_secret_provider = Selector(
        class_selector_config.llm_type,
        myapi=Singleton(DynamicSecretProvider, stackit_myapi_llm_settings),
        alephalpha=Singleton(StaticSecretProviderAlephAlpha, aleph_alpha_settings),
        ollama=Singleton(NoSecretProvider),
        stackit=Singleton(StaticSecretProviderStackit, stackit_vllm_settings),
    )
    key_value_store = Singleton(FileStatusKeyValueStore, key_value_store_settings)
    file_service = Singleton(S3Service, s3_settings=s3_settings)

    text_splitter = Singleton(RecursiveCharacterTextSplitter)(
        chunk_size=chunker_settings.max_size, chunk_overlap=chunker_settings.overlap
    )

    chunker = Singleton(TextChunker, text_splitter)
    extractor_api_configuration = Singleton(ExtractorConfiguration, host=document_extractor_settings.host)
    document_extractor_api_client = Singleton(ApiClient, extractor_api_configuration)
    document_extractor = Singleton(ExtractorApi, document_extractor_api_client)

    rag_api_configuration = Singleton(ExtractorConfiguration, host=rag_api_settings.host)
    rag_api_client = Singleton(RagApiClient, configuration=rag_api_configuration)
    rag_api = Singleton(RagApi, rag_api_client)

    information_mapper = Singleton(InformationPiece2Document)

    large_language_model = Selector(
        class_selector_config.llm_type,
        myapi=Singleton(llm_provider, aleph_alpha_settings),
        alephalpha=Singleton(llm_provider, aleph_alpha_settings),
        ollama=Singleton(llm_provider, ollama_settings, Ollama),
        stackit=Singleton(llm_provider, stackit_vllm_settings, VLLMOpenAI),
    )

    # Add secret provider to model
    large_language_model = Selector(
        class_selector_config.llm_type,
        myapi=Singleton(SecuredLLM, llm=large_language_model, secret_provider=llm_secret_provider),
        alephalpha=Singleton(SecuredLLM, llm=aleph_alpha_settings, secret_provider=llm_secret_provider),
        ollama=large_language_model,
        stackit=Singleton(SecuredLLM, llm=large_language_model, secret_provider=llm_secret_provider),
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

    langfuse_manager = Singleton(
        LangfuseManager,
        langfuse=langfuse,
        managed_prompts={
            LangchainSummarizer.__name__: SUMMARIZE_PROMPT,
        },
        llm=large_language_model,
    )

    summarizer = Singleton(
        LangchainSummarizer,
        langfuse_manager=langfuse_manager,
        chunker=summary_text_splitter,
        semaphore=Semaphore(summarizer_settings.maximum_concurrreny),
    )

    summary_enhancer = List(
        Singleton(PageSummaryEnhancer, summarizer),
        Singleton(SingleSummaryEnhancer, summarizer),
    )
    untraced_information_enhancer = Singleton(
        GeneralEnhancer,
        summary_enhancer,
    )
    information_enhancer = Singleton(
        LangfuseTracedChain,
        inner_chain=untraced_information_enhancer,
        settings=langfuse_settings,
    )
