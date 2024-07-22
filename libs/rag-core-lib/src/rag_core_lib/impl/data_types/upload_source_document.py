from pydantic import BaseModel, StrictStr
from rag_core_api.models.content_type import ContentType


class UploadSourceDocument(BaseModel):
    """
    Represents a document upload.

    Attributes:
        content_type (ContentType): The content type of the document.
        metadata (dict[str, str]): Additional metadata associated with the document.
        content (StrictStr): The content of the document.
    """

    content_type: ContentType
    metadata: dict[str, str]
    content: StrictStr
