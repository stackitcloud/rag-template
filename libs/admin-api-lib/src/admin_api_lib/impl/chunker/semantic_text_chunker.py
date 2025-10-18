"""Semantic text chunker backed by LangChain's semantic splitter."""

from __future__ import annotations

from collections.abc import Iterable
from inspect import signature
from typing import Any, Type

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import SemanticChunker as LangchainSemanticChunker

from admin_api_lib.chunker.chunker import Chunker


class SemanticTextChunker(Chunker):
    """Wrap the LangChain semantic chunker behind the local ``Chunker`` interface."""

    def __init__(
        self,
        embeddings: Embeddings,
        *,
        breakpoint_threshold_type: str | None = None,
        breakpoint_threshold: float | None = None,
        buffer_size: int | None = None,
        min_chunk_size: int | None = None,
        max_chunk_size: int | None = None,
        trim_chunks: bool | None = None,
        chunker_cls: Type[LangchainSemanticChunker] = LangchainSemanticChunker,
    ) -> None:
        """Initialise the semantic chunker.

        Parameters
        ----------
        embeddings : Embeddings
            The embeddings backend that powers semantic similarity detection.
        breakpoint_threshold_type : str | None, optional
            Strategy used to derive semantic breakpoints. Unsupported values are ignored.
        breakpoint_threshold : float | None, optional
            Threshold to apply for the selected breakpoint strategy. Unsupported values are ignored.
        buffer_size : int | None, optional
            Number of neighbouring sentences to include for context. Unsupported values are ignored.
        min_chunk_size : int | None, optional
            Minimum chunk size enforced by the chunker. Unsupported values are ignored.
        max_chunk_size : int | None, optional
            Maximum chunk size enforced by the chunker. Unsupported values are ignored.
        trim_chunks : bool | None, optional
            Whether to strip whitespace from chunk boundaries. Unsupported values are ignored.
        chunker_cls : type[LangchainSemanticChunker], optional
            Concrete semantic chunker implementation to instantiate. Defaults to
            :class:`langchain_text_splitters.SemanticChunker`.
        """

        init_params = _supported_parameters(chunker_cls)
        candidate_kwargs: dict[str, Any] = {
            "breakpoint_threshold_type": breakpoint_threshold_type,
            "breakpoint_threshold": breakpoint_threshold,
            "buffer_size": buffer_size,
            "min_chunk_size": min_chunk_size,
            "max_chunk_size": max_chunk_size,
            "trim_chunks": trim_chunks,
        }
        filtered_kwargs = {
            key: value
            for key, value in candidate_kwargs.items()
            if value is not None and key in init_params
        }

        self._semantic_chunker = chunker_cls(
            embeddings=embeddings,
            **filtered_kwargs,
        )

    def chunk(self, documents: Iterable[Document]) -> list[Document]:
        """Split documents using the configured semantic splitter.

        Parameters
        ----------
        documents : Iterable[Document]
            Documents to be chunked.

        Returns
        -------
        list[Document]
            Chunked documents produced by the semantic splitter.
        """

        documents_list = list(documents)
        if not documents_list:
            return []
        return self._semantic_chunker.split_documents(documents_list)


def _supported_parameters(chunker_cls: type) -> set[str]:
    """Return constructor parameters supported by ``chunker_cls``.

    Parameters
    ----------
    chunker_cls : type
        Semantic chunker class whose constructor signature should be inspected.

    Returns
    -------
    set[str]
        Set of keyword-parameter names accepted by the constructor.
    """

    try:
        params = signature(chunker_cls.__init__).parameters
    except (TypeError, ValueError):  # pragma: no cover - defensive, should not occur
        return set()
    return {name for name in params if name != "self"}
