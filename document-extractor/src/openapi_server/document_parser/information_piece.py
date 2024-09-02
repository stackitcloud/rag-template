"""Dataclass holding the information found in a document."""

import dataclasses

from openapi_server.document_parser.content_type import ContentType


@dataclasses.dataclass
class InformationPiece:
    """Dataclass holding the information found in a document."""

    content_type: ContentType
    metadata: dict  # should contain at least "document" and "page"
    content_text: str | None = None  # text content
