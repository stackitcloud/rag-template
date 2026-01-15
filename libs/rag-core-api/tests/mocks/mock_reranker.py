"""Provide a mock reranker for CompositeRetriever unit tests."""

__all__ = ["MockReranker"]


class MockReranker:
    """Provide a simple reranker test double.

    The mock records whether it was invoked and returns a deterministic top-2 subset.
    """

    def __init__(self):
        self.invoked = False

    async def ainvoke(self, payload, config=None):
        """Return a reranked subset of the provided documents.

        Parameters
        ----------
        payload : tuple
            A ``(documents, query)`` tuple.
        config : Any, optional
            Optional runtime config passed through by the caller.

        Returns
        -------
        list
            The top two documents sorted by score when available.
        """
        self.invoked = True
        documents, _query = payload
        # Emulate reranker selecting top 2 with highest 'score' if present; else first 2 reversed
        if all("score" in d.metadata for d in documents):
            docs_sorted = sorted(documents, key=lambda d: d.metadata["score"], reverse=True)
        else:  # pragma: no cover - fallback path
            docs_sorted = list(reversed(documents))
        return docs_sorted[:2]
