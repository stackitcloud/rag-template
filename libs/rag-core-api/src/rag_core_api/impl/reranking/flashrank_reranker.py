from typing import Optional

from langchain_community.document_compressors.flashrank_rerank import FlashrankRerank
from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig

from rag_core_api.reranking.reranker import Reranker, RerankerInput, RerankerOutput


class FlashrankReranker(Reranker):

    def __init__(self, reranker: FlashrankRerank, **kwargs):
        super().__init__(**kwargs)
        self._reranker = reranker

    def invoke(self, rerank_input: RerankerInput, config: Optional[RunnableConfig] = None) -> RerankerOutput:
        input_documents, question = rerank_input
        reranked = self._reranker.compress_documents(documents=input_documents, query=question)
        return [self._re_add_metadata(input_documents, x) for x in reranked]

    def _re_add_metadata(
        self,
        all_documents: list[Document],
        relevant_document: Document,
    ) -> Document:
        # TODO: This is only needed because langchains wrapper around FlashRerank
        # is destructive in terms of metadata. This could be fixed in their wrapper implementation.
        for doc in all_documents:
            if doc.page_content == relevant_document.page_content:
                relevant_document.metadata = doc.metadata | {
                    "relevance_score": relevant_document.metadata["relevance_score"]
                }
                return relevant_document
        raise Exception("Something went really wrong. The retrieved document could not be found after re-ranking.")
