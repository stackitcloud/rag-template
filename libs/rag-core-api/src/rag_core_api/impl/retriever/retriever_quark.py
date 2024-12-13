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
    TYPE_KEY = "type"

    def __init__(
        self,
        vector_database: VectorDatabase,
        retriever_type: ContentType,
        k: int = 10,
        threshold: float = 0.3,
        **kwargs,
    ):
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
        """Check if the vector db contains a non-empty collection with the expected name."""
        if not self._vector_database.collection_available:
            raise NoOrEmptyCollectionError()

    async def ainvoke(self, retriever_input: str, config: Optional[RunnableConfig] = None) -> list[Document]:
        config = ensure_config(config)
        self.verify_readiness()
        if self.TYPE_KEY not in config["metadata"]["filter_kwargs"].keys():
            config["metadata"]["filter_kwargs"] = config["metadata"]["filter_kwargs"] | self._filter_kwargs
        return await self._vector_database.asearch(
            query=retriever_input,
            search_kwargs=self._search_kwargs,
            filter_kwargs=config["metadata"]["filter_kwargs"],
        )
