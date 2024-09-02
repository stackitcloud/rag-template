from typing import List
from openapi_server.document_parser.information_piece import InformationPiece as InternalInformationPiece
from openapi_server.models.meta_information_piece import MetaInformationPiece
from openapi_server.models.information_piece import InformationPiece as ExternalInformationPiece
from openapi_server.models.information_type import InformationType as ExternalInformationType
from openapi_server.document_parser.content_type import ContentType as InternalInformationType


class Internal2ExternalInformationPiece:
    TYPE_LOOKUP_TABLE = {
        InternalInformationType.IMAGE: ExternalInformationType.IMAGE,
        InternalInformationType.TEXT: ExternalInformationType.TEXT,
        InternalInformationType.TABLE: ExternalInformationType.TABLE,
    }

    def map(self, internal: InternalInformationPiece) -> ExternalInformationPiece:
        information_type = self._map_information_type(internal.content_type)
        meta = self._map_meta(internal.metadata)
        return ExternalInformationPiece(
            content=internal.content_text, type=information_type.name, meta_information=meta
        )

    def _map_information_type(self, internal: InternalInformationType) -> ExternalInformationType:
        return self.TYPE_LOOKUP_TABLE[internal]

    def _map_meta(self, internal: dict) -> List[MetaInformationPiece]:
        return [MetaInformationPiece(Key=key, Value=value) for key, value in internal.items()]
