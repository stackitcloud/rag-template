"""Mock reranker used by CompositeRetriever unit tests."""

from langchain_core.documents import Document

__all__ = ["MockReranker"]


class MockReranker:
    def __init__(self):
        self.invoked = False

    async def ainvoke(self, payload, config=None):  # noqa: D401
        self.invoked = True
        documents, _query = payload
        # Emulate reranker selecting top 2 with highest 'score' if present; else first 2 reversed
        if all("score" in d.metadata for d in documents):
            docs_sorted = sorted(documents, key=lambda d: d.metadata["score"], reverse=True)
        else:  # pragma: no cover - fallback path
            docs_sorted = list(reversed(documents))
        return docs_sorted[:2]
