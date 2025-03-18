"""Module for the VectorDatabase abstract class."""

from abc import ABC, abstractmethod

from langchain_community.vectorstores import VectorStore
from langchain_core.documents import Document
from langchain_qdrant import SparseEmbeddings

from rag_core_api.embeddings.embedder import Embedder
from rag_core_api.impl.settings.vector_db_settings import VectorDatabaseSettings


class VectorDatabase(ABC):
    """Abstract base class for a vector database."""

    def __init__(
        self,
        settings: VectorDatabaseSettings,
        embedder: Embedder,
        sparse_embedder: SparseEmbeddings,
        vectorstore: VectorStore,
    ):
        """
        Initialize the vector database.

        Parameters
        ----------
        settings : VectorDatabaseSettings
            The settings for the vector database.
        embedder : Embedder
            The embedder used to convert chunks into vector representations.
        vectorstore : Qdrant
            The Qdrant vector store instance.
        """
        self._settings = settings
        self._embedder = embedder
        self._sparse_embedder = sparse_embedder
        self._vectorstore = vectorstore

    @property
    @abstractmethod
    def collection_available(self) -> bool:
        """Check if the collection is available in the vector database.

        Returns
        -------
        bool
            True if the collection is available, False otherwise.

        Raises
        ------
        NotImplementedError
            If the method is not implemented.
        """
        raise NotImplementedError()

    @abstractmethod
    async def asearch(self, query: str, search_kwargs: dict, filter_kwargs: dict) -> list[Document]:
        """Search in a vector database for points fitting the query and the search_kwargs.

        Parameters
        ----------
        query : str
            The search query string.
        search_kwargs : dict
            Additional keyword arguments for the search.
        filter_kwargs : dict, optional
            Optional filter keyword arguments to refine the search.

        Returns
        -------
        list[Document]
            List of langchain documents.

        Raises
        ------
        NotImplementedError
            If the method is not implemented.
        """
        raise NotImplementedError()

    @abstractmethod
    def upload(self, documents: list[Document]):
        """Upload the documents to the vector database.

        Parameters
        ----------
        documents : list[Document]
            List of documents which will be uploaded.

        Raises
        ------
        NotImplementedError
            If the method is not implemented.
        """
        raise NotImplementedError()

    @abstractmethod
    def delete(self, delete_request: dict) -> None:
        """
        Delete the documents from the vector database.

        Parameters
        ----------
        delete_request : dict
            Contains the information required for deleting the documents.

        Raises
        ------
        NotImplementedError
            If the method is not implemented.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_collections(self) -> list[str]:
        """
        Get all collection names from the vector database.

        Returns
        -------
        list[str]
            List of all collection names.

        Raises
        ------
        NotImplementedError
            If the method is not implemented.
        """
        raise NotImplementedError()
