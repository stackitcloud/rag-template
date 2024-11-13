from extractor_api_lib.document_parser.information_piece import InformationPiece as InternalInformationPiece
from extractor_api_lib.models.key_value_pair import KeyValuePair as MetaInformationPiece
from extractor_api_lib.models.information_piece import InformationPiece as ExternalInformationPiece
from extractor_api_lib.models.content_type import ContentType as ExternalContentType
from extractor_api_lib.document_parser.content_type import ContentType as InternalContentType


class Internal2ExternalInformationPiece:
    TYPE_LOOKUP_TABLE = {
        InternalContentType.IMAGE: ExternalContentType.IMAGE,
        InternalContentType.TEXT: ExternalContentType.TEXT,
        InternalContentType.TABLE: ExternalContentType.TABLE,
    }

    def map_internal_to_external(self, internal: InternalInformationPiece) -> ExternalInformationPiece:
        information_type = self._map_information_type(internal.type)
        meta = self._map_meta(internal.metadata)
        return ExternalInformationPiece(page_content=internal.page_content, type=information_type, metadata=meta)

    def _map_information_type(self, internal: InternalContentType) -> ExternalContentType:
        return self.TYPE_LOOKUP_TABLE[internal]

    def _map_meta(self, internal: dict) -> list[MetaInformationPiece]:
        return [MetaInformationPiece(key=key, value=value) for key, value in internal.items()]
