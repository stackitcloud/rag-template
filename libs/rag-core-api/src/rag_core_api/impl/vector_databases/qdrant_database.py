from langchain_qdrant import Qdrant
from langchain_core.documents import Document
from qdrant_client.http import models
from qdrant_client.models import Filter, FieldCondition, MatchValue

from rag_core_api.embeddings.embedder import Embedder
from rag_core_api.impl.settings.vector_db_settings import VectorDatabaseSettings
from rag_core_api.vector_databases.vector_database import VectorDatabase


class QdrantDatabase(VectorDatabase):
    """
    A class representing the interface to the Qdrant database.

    Inherits from VectorDatabase.
    """

    def __init__(
        self,
        settings: VectorDatabaseSettings,
        embedder: Embedder,
        vectorstore: Qdrant,
    ):
        """
        Initialize the Qdrant database.

        Args:
            settings: The settings for the vector database.
            chunker: The chunker used to split documents into smaller chunks.
            embedder: The embedder used to convert chunks into vector representations.
        """
        super().__init__(
            settings=settings,
            embedder=embedder,
            vectorstore=vectorstore,
        )

    @property
    def collection_available(self):
        if self._vectorstore.collection_name in [c.name for c in self.get_collections()]:
            collection = self._vectorstore.client.get_collection(self._vectorstore.collection_name)
            return collection.points_count > 0
        return False

    @staticmethod
    def _search_kwargs_builder(search_kwargs: dict, filter_kwargs: dict):
        return search_kwargs | {"filter": filter_kwargs}

    async def asearch(self, query: str, search_kwargs: dict, filter_kwargs: dict | None = None) -> list[Document]:
        retriever = self._vectorstore.as_retriever(
            query=query,
            search_kwargs=(
                search_kwargs
                if not filter_kwargs
                else self._search_kwargs_builder(search_kwargs=search_kwargs, filter_kwargs=filter_kwargs)
            ),
        )
        results = await retriever.ainvoke(query)
        related_results = []
        for res in results:
            related_results += self._get_related(res.metadata["related"])
        return results + related_results

    def get_specific_document(self, document_id: str) -> list[Document]:
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

        Args:
            documents (list[Document]): The list of documents to be saved.

        Returns:
            None
        """
        Qdrant.from_documents(
            documents,
            self._embedder.get_embedder(),
            collection_name=self._settings.collection_name,
            url=self._settings.url,
        )

    def delete(self, delete_request: dict) -> None:
        """
        Delete all points associated with a specific document from the Qdrant database.

        Args:
            document_name (str): The name of the document whose points are to be deleted.
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
        Get all collection names from the vector database
        """
        return self._vectorstore.client.get_collections().collections

    def _get_related(self, related_ids: list[str]) -> list[Document]:
        result = []
        for document_id in related_ids:
            result += self.get_specific_document(document_id)
        return result
