from abc import ABC, abstractmethod

from langchain_core.documents import Document


class Chunker(ABC):
    """
    Abstract base class for chunking documents into smaller parts.
    """

    @abstractmethod
    def chunk(self, documents: Document) -> list[Document]:
        """
        Abstract method to chunk the given documents into smaller parts.

        Args:
            documents (Document): The documents to be chunked.

        Returns:
            List[Document]: A list of smaller parts obtained by chunking the documents.
        """
