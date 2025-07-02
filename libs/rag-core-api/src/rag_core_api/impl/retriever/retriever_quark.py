"""Module for the RetrieverQuark class."""

import logging
from typing import Optional

from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig, ensure_config

from rag_core_api.impl.retriever.no_or_empty_collection_error import (
    NoOrEmptyCollectionError,
)
from rag_core_api.retriever.retriever import Retriever
from rag_core_api.vector_databases.vector_database import VectorDatabase
from rag_core_lib.impl.data_types.content_type import ContentType

logger = logging.getLogger(__name__)


class RetrieverQuark(Retriever):
    """
    RetrieverQuark class for retrieving documents from a vector database.

    Attributes
    ----------
    TYPE_KEY : str
        The key used for the type of content in filter_kwargs.
    """

    TYPE_KEY = "type"

    def __init__(
        self,
        vector_database: VectorDatabase,
        retriever_type: ContentType,
        k: int = 10,
        threshold: float = 0.3,
        **kwargs,
    ):
        """
        Initialize the RetrieverQuark.

        Parameters
        ----------
        vector_database : VectorDatabase
            The vector database instance to be used for retrieval.
        retriever_type : ContentType
            The type of content to be retrieved.
        k : int, optional
            The number of top results to retrieve (default 10).
        threshold : float, optional
            The score threshold for filtering results (default 0.3).
        **kwargs
            Additional keyword arguments to pass to the superclass initializer.
        """
        super().__init__(**kwargs)
        self._vector_database = vector_database
        self._search_kwargs = {
            "k": k,
            "score_threshold": threshold,
        }
        self._filter_kwargs = {
            self.TYPE_KEY: retriever_type.value,
        }

    def verify_readiness(self) -> None:
        """
        Verify the readiness of the vector database.

        This method checks if the vector database contains a non-empty collection with the expected name.
        If the collection is not available or is empty, it raises a NoOrEmptyCollectionError.

        Raises
        ------
        NoOrEmptyCollectionError
            If the vector database does not contain a non-empty collection with the expected name.
        """
        if not self._vector_database.collection_available:
            raise NoOrEmptyCollectionError()

    async def ainvoke(self, retriever_input: str, config: Optional[RunnableConfig] = None) -> list[Document]:
        """
        Asynchronously invokes the retriever with the given input and configuration.

        Parameters
        ----------
        retriever_input : str
            The input string to be used for retrieval.
        config : Optional[RunnableConfig]
            The configuration for the retrieval process (default None).

        Returns
        -------
        list[Document]
            A list of Document objects retrieved based on the input and configuration.
        """
        config = ensure_config(config)
        self.verify_readiness()
        if self.TYPE_KEY not in config["metadata"]["filter_kwargs"].keys():
            config["metadata"]["filter_kwargs"] = config["metadata"]["filter_kwargs"] | self._filter_kwargs
        return await self._vector_database.asearch(
            query=retriever_input,
            search_kwargs=self._search_kwargs,
            filter_kwargs=config["metadata"]["filter_kwargs"],
        )
