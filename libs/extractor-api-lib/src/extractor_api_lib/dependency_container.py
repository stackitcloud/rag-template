"""Module for dependency injection container for managing application dependencies."""

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Factory, List, Singleton  # noqa: WOT001

from extractor_api_lib.impl.api_endpoints.general_file_extractor import (
    GeneralFileExtractor,
)
from extractor_api_lib.impl.api_endpoints.general_source_extractor import (
    GeneralSourceExtractor,
)
from extractor_api_lib.impl.extractors.confluence_extractor import ConfluenceExtractor
from extractor_api_lib.impl.extractors.file_extractors.epub_extractor import (
    EpubExtractor,
)
from extractor_api_lib.impl.extractors.file_extractors.ms_docs_extractor import (
    MSDocsExtractor,
)
from extractor_api_lib.impl.extractors.file_extractors.pdf_extractor import PDFExtractor
from extractor_api_lib.impl.extractors.file_extractors.xml_extractor import XMLExtractor
from extractor_api_lib.impl.extractors.sitemap_extractor import SitemapExtractor
from extractor_api_lib.impl.file_services.s3_service import S3Service
from extractor_api_lib.impl.mapper.confluence_langchain_document2information_piece import (
    ConfluenceLangchainDocument2InformationPiece,
)
from extractor_api_lib.impl.mapper.internal2external_information_piece import (
    Internal2ExternalInformationPiece,
)
from extractor_api_lib.impl.mapper.langchain_document2information_piece import (
    LangchainDocument2InformationPiece,
)
from extractor_api_lib.impl.mapper.sitemap_document2information_piece import (
    SitemapLangchainDocument2InformationPiece,
)
from extractor_api_lib.impl.settings.pdf_extractor_settings import PDFExtractorSettings
from extractor_api_lib.impl.settings.s3_settings import S3Settings
from extractor_api_lib.impl.table_converter.dataframe2markdown import DataFrame2Markdown
from extractor_api_lib.impl.utils.sitemap_extractor_utils import (
    custom_sitemap_metadata_parser_function,
    custom_sitemap_parser_function,
)


class DependencyContainer(DeclarativeContainer):
    """Dependency injection container for managing application dependencies."""

    # Settings
    settings_s3 = S3Settings()
    settings_pdf_extractor = PDFExtractorSettings()

    sitemap_parsing_function = Factory(lambda: custom_sitemap_parser_function)
    sitemap_meta_function = Factory(lambda: custom_sitemap_metadata_parser_function)

    database_converter = Singleton(DataFrame2Markdown)
    file_service = Singleton(S3Service, settings_s3)
    pdf_extractor = Singleton(PDFExtractor, file_service, settings_pdf_extractor, database_converter)
    ms_docs_extractor = Singleton(MSDocsExtractor, file_service, database_converter)
    xml_extractor = Singleton(XMLExtractor, file_service)

    intern2external = Singleton(Internal2ExternalInformationPiece)
    confluence_document2information_piece = Singleton(ConfluenceLangchainDocument2InformationPiece)
    langchain_document2information_piece = Singleton(LangchainDocument2InformationPiece)
    sitemap_document2information_piece = Singleton(SitemapLangchainDocument2InformationPiece)
    epub_extractor = Singleton(EpubExtractor, file_service, langchain_document2information_piece)

    file_extractors = List(pdf_extractor, ms_docs_extractor, xml_extractor, epub_extractor)

    general_file_extractor = Singleton(GeneralFileExtractor, file_service, file_extractors, intern2external)
    confluence_extractor = Singleton(ConfluenceExtractor, mapper=confluence_document2information_piece)

    sitemap_extractor = Singleton(
        SitemapExtractor,
        mapper=sitemap_document2information_piece,
        parsing_function=sitemap_parsing_function,
        meta_function=sitemap_meta_function,
    )
    source_extractor = Singleton(
        GeneralSourceExtractor,
        mapper=intern2external,
        available_extractors=List(confluence_extractor, sitemap_extractor),
    )
