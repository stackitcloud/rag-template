from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Singleton, List

from openapi_server.document_parser.table_coverters.dataframe2markdown import DataFrame2Markdown
from openapi_server.document_parser.xml_extractor import XMLExtractor
from openapi_server.document_parser.ms_docs_extractor import MSDocsExtractor
from openapi_server.document_parser.general_extractor import GeneralExtractor
from openapi_server.document_parser.pdf_extractor import PDFExtractor
from openapi_server.file_services.s3_service import S3Service
from openapi_server.impl.mapper.internal2external_information_piece import Internal2ExternalInformationPiece
from openapi_server.settings.pdf_extractor_settings import PDFExtractorSettings
from openapi_server.settings.s3_settings import S3Settings
from openapi_server.impl import extractor_api_impl


class Container(DeclarativeContainer):
    """
    Dependency injection container for managing application dependencies.
    """

    wiring_config = WiringConfiguration(modules=[extractor_api_impl])

    # Settings
    settings_s3 = Singleton(S3Settings)
    settings_pdf_extractor = Singleton(PDFExtractorSettings)

    database_converter = Singleton(DataFrame2Markdown)
    file_service = Singleton(S3Service, settings_s3)
    pdf_extractor = Singleton(PDFExtractor, file_service, settings_pdf_extractor, database_converter)
    ms_docs_extractor = Singleton(MSDocsExtractor, file_service, database_converter)
    xml_extractor = Singleton(XMLExtractor, file_service)

    intern2external = Singleton(Internal2ExternalInformationPiece)
    all_extractors = List(pdf_extractor, ms_docs_extractor, xml_extractor)

    general_extractor = Singleton(GeneralExtractor, file_service, all_extractors)
