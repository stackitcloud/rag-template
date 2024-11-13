from abc import ABC, abstractmethod

from fastapi import Response


class DocumentReferenceRetriever(ABC):
    """Abstract base class for retrieving document references."""

    @abstractmethod
    async def adocument_reference_id_get(self, identification: str) -> Response:
        """Get document reference by ID."""
        pass
