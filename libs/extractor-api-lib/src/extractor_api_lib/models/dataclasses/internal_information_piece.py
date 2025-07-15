"""Module containing the InformationPiece dataclass."""

import dataclasses

from extractor_api_lib.impl.types.content_type import ContentType


@dataclasses.dataclass
class InternalInformationPiece:
    """Dataclass holding the information found in a document."""

    type: ContentType  # noqa: A003  # type of the information
    metadata: dict  # should contain at least "document" and "page"
    page_content: str | None = None  # page content
