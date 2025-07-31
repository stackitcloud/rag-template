"""Module for the Flashrank reranker implementation."""

from typing import Optional

from langchain_community.document_compressors.flashrank_rerank import FlashrankRerank
from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig

from rag_core_api.reranking.reranker import Reranker, RerankerInput, RerankerOutput


class FlashrankReranker(Reranker):
    """FlashrankReranker reranks documents.

    It is a class that provides functionality to rerank documents
    based on a given question using the FlashrankRerank algorithm.
    """

    def __init__(self, reranker: FlashrankRerank, **kwargs):
        """
        Initialize the FlashrankReranker.

        Parameters
        ----------
        reranker : FlashrankRerank
            An instance of the FlashrankRerank class.
        **kwargs : dict
            Additional keyword arguments passed to the superclass initializer.
        """
        super().__init__(**kwargs)
        self._reranker = reranker

    async def ainvoke(self, rerank_input: RerankerInput, config: Optional[RunnableConfig] = None) -> RerankerOutput:
        """
        Asynchronously invokes the reranker to rerank the input documents based on the given question.

        Parameters
        ----------
        rerank_input : RerankerInput
            A tuple containing the input documents and the question for reranking.
        config : Optional[RunnableConfig]
            Configuration for the runnable (default None).

        Returns
        -------
        RerankerOutput
            A list of reranked documents with metadata re-added.
        """
        input_documents, question = rerank_input
        reranked = await self._reranker.acompress_documents(documents=input_documents, query=question)
        return [self._re_add_metadata(input_documents, x) for x in reranked]

    def _re_add_metadata(
        self,
        all_documents: list[Document],
        relevant_document: Document,
    ) -> Document:
        # NOTE: This is only needed because langchains wrapper around FlashRerank
        # is destructive in terms of metadata. This could be fixed in their wrapper implementation.
        for doc in all_documents:
            if doc.page_content == relevant_document.page_content:
                relevant_document.metadata = doc.metadata | {
                    "relevance_score": relevant_document.metadata["relevance_score"]
                }
                return relevant_document
        raise Exception("Something went really wrong. The retrieved document could not be found after re-ranking.")
