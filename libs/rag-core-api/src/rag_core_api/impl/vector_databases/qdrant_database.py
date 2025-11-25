"""Module containing the QdrantDatabase class."""

import logging

from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore, SparseEmbeddings
from qdrant_client.http import models
from qdrant_client.models import FieldCondition, Filter, MatchValue

from rag_core_api.embeddings.embedder import Embedder
from rag_core_api.impl.settings.vector_db_settings import VectorDatabaseSettings
from rag_core_api.vector_databases.vector_database import VectorDatabase


logger = logging.getLogger(__name__)


class QdrantDatabase(VectorDatabase):
    """
    A class representing the interface to the Qdrant database.

    Inherits from VectorDatabase.
    """

    def __init__(
        self,
        settings: VectorDatabaseSettings,
        embedder: Embedder,
        sparse_embedder: SparseEmbeddings,
        vectorstore: QdrantVectorStore,
    ):
        """
        Initialize the Qdrant database.

        Parameters
        ----------
        settings : VectorDatabaseSettings
            The settings for the vector database.
        embedder : Embedder
            The embedder used to convert chunks into vector representations.
        vectorstore : Qdrant
            The Qdrant vector store instance.
        """
        super().__init__(
            settings=settings,
            embedder=embedder,
            vectorstore=vectorstore,
            sparse_embedder=sparse_embedder,
        )

    @property
    def collection_available(self):
        """
        Check if the collection is available and has points.

        This property checks if the collection specified by the `_vectorstore.collection_name`
        exists in the list of collections and if it contains any points.

        Returns
        -------
        bool
            True if the collection exists and has points, False otherwise.
        """
        if self._vectorstore.collection_name in [c.name for c in self.get_collections()]:
            collection = self._vectorstore.client.get_collection(self._vectorstore.collection_name)
            return collection.points_count > 0
        return False

    @staticmethod
    def _search_kwargs_builder(search_kwargs: dict, filter_kwargs: dict):
        """Build search kwargs with proper Qdrant filter format."""
        if not filter_kwargs:
            return search_kwargs

        # Convert dict filter to Qdrant filter format
        qdrant_filter = models.Filter(
            must=[
                models.FieldCondition(key="metadata." + key, match=models.MatchValue(value=value))
                for key, value in filter_kwargs.items()
            ]
        )

        return {**search_kwargs, "filter": qdrant_filter}

    async def asearch(self, query: str, search_kwargs: dict, filter_kwargs: dict | None = None) -> list[Document]:
        """
        Asynchronously search for documents based on a query and optional filters.

        Parameters
        ----------
        query : str
            The search query string.
        search_kwargs : dict
            Additional keyword arguments for the search.
        filter_kwargs : dict, optional
            Optional filter keyword arguments to refine the search (default is None).

        Returns
        -------
        list[Document]
            A list of documents that match the search query and filters, including related documents.
        """
        try:
            search_params = self._search_kwargs_builder(search_kwargs=search_kwargs, filter_kwargs=filter_kwargs)

            retriever = self._vectorstore.as_retriever(query=query, search_kwargs=search_params)

            results = await retriever.ainvoke(query)
            related_results = []

            for res in results:
                related_results += self._get_related(res.metadata["related"])
            return results + related_results

        except Exception:
            logger.exception("Search failed")
            raise

    def get_specific_document(self, document_id: str) -> list[Document]:
        """
        Retrieve a specific document from the vector database using the document ID.

        Parameters
        ----------
        document_id : str
            The ID of the document to retrieve.

        Returns
        -------
        list[Document]
            A list containing the requested document as a Document object. If the document is not found,
            an empty list is returned.
        """
        requested = self._vectorstore.client.scroll(
            collection_name=self._vectorstore.collection_name,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="metadata.id",
                        match=MatchValue(value=document_id),
                    )
                ]
            ),
        )
        if not requested:
            return []
        # convert to Document
        return [
            (
                Document(
                    page_content=search_result.payload["page_content"],
                    metadata=search_result.payload["metadata"],
                )
            )
            for search_result in requested[0]
        ]

    def upload(self, documents: list[Document]) -> None:
        """
        Save the given documents to the Qdrant database.

        Parameters
        ----------
        documents : list[Document]
            The list of documents to be stored.

        Returns
        -------
        None
        """
        self._vectorstore = self._vectorstore.from_documents(
            documents,
            embedding=self._embedder.get_embedder(),
            sparse_embedding=self._sparse_embedder,
            location=self._settings.location,
            collection_name=self._settings.collection_name,
            retrieval_mode=self._settings.retrieval_mode,
        )

    def delete(self, delete_request: dict) -> None:
        """
        Delete all points associated with a specific document from the Qdrant database.

        Parameters
        ----------
        delete_request : dict
            A dictionary containing the conditions to match the points to be deleted. Each key-value pair
            represents a field and its corresponding value to match.

        Returns
        -------
        None
        """
        filter_conditions = [
            models.FieldCondition(
                key=key,
                match=models.MatchValue(value=value),
            )
            for key, value in delete_request.items()
        ]

        points_selector = models.FilterSelector(
            filter=models.Filter(
                must=filter_conditions,
            )
        )

        self._vectorstore.client.delete(
            collection_name=self._settings.collection_name,
            points_selector=points_selector,
        )

    def get_collections(self) -> list[str]:
        """
        Get all collection names from the vector database.

        Returns
        -------
        list[str]
            A list of collection names from the vector database.
        """
        return self._vectorstore.client.get_collections().collections

    def _get_related(self, related_ids: list[str]) -> list[Document]:
        result = []
        for document_id in related_ids:
            result += self.get_specific_document(document_id)
        return result
