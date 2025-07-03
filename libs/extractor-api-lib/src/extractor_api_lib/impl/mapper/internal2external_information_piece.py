"""Module for mapping internal information piece to external information piece."""

from extractor_api_lib.impl.types.content_type import ContentType as InternalContentType
from extractor_api_lib.models.content_type import ContentType as ExternalContentType
from extractor_api_lib.models.dataclasses.internal_information_piece import InternalInformationPiece
from extractor_api_lib.models.information_piece import InformationPiece
from extractor_api_lib.models.key_value_pair import KeyValuePair as MetaInformationPiece


class Internal2ExternalInformationPiece:
    """
    A class to map internal information pieces to external information pieces.

    Attributes
    ----------
    TYPE_LOOKUP_TABLE : dict
        A dictionary mapping internal content types to external content types.
    """

    TYPE_LOOKUP_TABLE = {
        InternalContentType.IMAGE: ExternalContentType.IMAGE,
        InternalContentType.TEXT: ExternalContentType.TEXT,
        InternalContentType.TABLE: ExternalContentType.TABLE,
    }

    def map_internal_to_external(self, internal: InternalInformationPiece) -> InformationPiece:
        """Map an InternalInformationPiece object to an ExternalInformationPiece object.

        Parameters
        ----------
        internal : InternalInformationPiece
            The internal information piece to be mapped.

        Returns
        -------
        ExternalInformationPiece
            The mapped external information piece.
        """
        information_type = self._map_information_type(internal.type)
        meta = self._map_meta(internal.metadata)
        return InformationPiece(page_content=internal.page_content, type=information_type, metadata=meta)

    def _map_information_type(self, internal: InternalContentType) -> ExternalContentType:
        return self.TYPE_LOOKUP_TABLE[internal]

    def _map_meta(self, internal: dict) -> list[MetaInformationPiece]:
        return [MetaInformationPiece(key=key, value=value) for key, value in internal.items()]
