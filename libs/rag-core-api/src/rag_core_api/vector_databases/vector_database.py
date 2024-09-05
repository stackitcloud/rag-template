from abc import ABC, abstractmethod

from langchain_core.documents import Document
from langchain_community.vectorstores import VectorStore

from rag_core_api.embeddings.embedder import Embedder
from rag_core_api.impl.settings.vector_db_settings import VectorDatabaseSettings


class VectorDatabase(ABC):
    def __init__(
        self,
        settings: VectorDatabaseSettings,
        embedder: Embedder,
        vectorstore: VectorStore,
    ):
        """
        Initialize the vector database.

        Args:
            settings: The settings for the vector database.
            embedder: The embedder used to convert chunks into vector representations.
        """
        self._settings = settings
        self._embedder = embedder
        self._vectorstore = vectorstore

    @property
    @abstractmethod
    def collection_available(self) -> bool:
        """Check if the collection is available in the vector database.

        Returns:
            bool: True if the collection is available, False otherwise.

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError()

    @abstractmethod
    def search(self, query: str, search_kwargs: dict, filter_kwargs: dict) -> list[Document]:
        """Search in a vectordatabase for points fitting the query and the search_kwargs.

        Args:
            query (str): Query string
            search_kwargs (dict): Search arguments

        Return:
            List of langchain documents

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError()

    @abstractmethod
    def upload(self, documents: list[Document]):
        """Uploads the documents to the vector database.

        Args:
            documents (list[Document]): List of documents which will be uploaded

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError()

    @abstractmethod
    def delete(self, delete_request: dict) -> None:
        """Deletes the documents from the vector database.

        Args:
            delete_request (dict): Contains the information required for deleting the documents.

        Raises:
            NotImplementedError: This method is meant to be overridden by subclasses.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_collections(self) -> list[str]:
        """
        Get all collection names from the vector database
        """
        raise NotImplementedError()
