import logging
from typing import Any, List, Optional
from copy import deepcopy

from langchain_core.documents import Document
from langchain_core.runnables import (
    RunnableConfig,
)
from rag_core_lib.impl.data_types.content_type import ContentType

from rag_core_api.retriever.retriever import Retriever
from rag_core_api.impl.retriever.no_documents_error import NoDocumentsError
from rag_core_api.impl.retriever.retriever_quark import RetrieverQuark

logger = logging.getLogger(__name__)


class CompositeRetriever(Retriever):
    def __init__(
        self,
        retrievers: list[RetrieverQuark],
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._retrievers = retrievers

    def verify_readiness(self) -> None:
        """Check if the vector db contains a non-empty collection with the expected name."""
        for retriever in self._retrievers:
            retriever.verify_readiness()

    def invoke(self, input: str, config: Optional[RunnableConfig] = None, **kwargs: Any) -> List[Document]:
        results = []
        for retriever in self._retrievers:
            tmp_config = deepcopy(config)
            results += retriever.invoke(input, config=tmp_config)

        # remove summaries
        results = [x for x in results if x.metadata["type"] != ContentType.SUMMARY.value]

        # remove duplicated entries
        return_val = []
        for result in results:
            if result.metadata["id"] in [x.metadata["id"] for x in return_val]:
                continue
            return_val.append(result)

        if not return_val:
            raise NoDocumentsError()

        return return_val
