"""Semantic text chunker backed by LangChain's semantic splitter.

Adds optional max/min chunk size enforcement via RecursiveCharacterTextSplitter
when both values are provided and ``max_chunk_size > min_chunk_size``.
"""

from __future__ import annotations

from collections.abc import Iterable
import re
from inspect import signature
from typing import Any, Type
import logging

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_experimental.text_splitter import SemanticChunker as LangchainSemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from nltk.tokenize import PunktSentenceTokenizer

from admin_api_lib.chunker.chunker import Chunker


logger = logging.getLogger(__name__)


class SemanticTextChunker(Chunker):
    """Semantic text chunker backed by LangChain's semantic splitter with optional max/min chunk size enforcement."""

    def __init__(
        self,
        embeddings: Embeddings,
        *,
        breakpoint_threshold_type: str | None = None,
        breakpoint_threshold_amount: float | None = None,
        buffer_size: int | None = None,
        min_chunk_size: int | None = None,
        max_chunk_size: int | None = None,
        overlap: int | None = None,
        chunker_cls: Type[LangchainSemanticChunker] = LangchainSemanticChunker,
        recursive_text_splitter: RecursiveCharacterTextSplitter | None = None,
    ) -> None:
        """Initialise the semantic chunker.

        Parameters
        ----------
        embeddings : Embeddings
            The embeddings backend that powers semantic similarity detection.
        breakpoint_threshold_type : str | None, optional
            Strategy used to derive semantic breakpoints.
        breakpoint_threshold_amount : float | None, optional
            Threshold to apply for the selected breakpoint strategy.
        buffer_size : int | None, optional
            Number of neighbouring sentences to include for context.
        min_chunk_size : int | None, optional
            Minimum chunk size enforced by the chunker.
        max_chunk_size : int | None, optional
            Maximum chunk size enforced by the chunker.
        overlap : int | None, optional
            Number of overlapping characters between chunks.
        chunker_cls : type[LangchainSemanticChunker], optional
            Concrete semantic chunker implementation to instantiate. Defaults to
            :class:`langchain_text_splitters.SemanticChunker`.
        recursive_text_splitter : RecursiveCharacterTextSplitter | None, optional
            Optional pre-configured recursive text splitter to use for max/min chunk size enforcement.
        """
        self._min_chunk_size = min_chunk_size
        self._max_chunk_size = max_chunk_size
        self._overlap = overlap

        init_params = _supported_parameters(chunker_cls)
        candidate_kwargs: dict[str, Any] = {
            "breakpoint_threshold_type": breakpoint_threshold_type,
            "breakpoint_threshold_amount": breakpoint_threshold_amount,
            "buffer_size": buffer_size,
            "min_chunk_size": min_chunk_size,
        }
        filtered_kwargs = {
            key: value for key, value in candidate_kwargs.items() if value is not None and key in init_params
        }

        self._semantic_chunker = chunker_cls(
            embeddings=embeddings,
            **filtered_kwargs,
        )

        # Configure a recursive splitter for max/min enforcement when requested.
        # If none provided, instantiate a sensible default using max_chunk_size and overlap.
        self._recursive_splitter: RecursiveCharacterTextSplitter | None = None
        if self._min_chunk_size and self._max_chunk_size and self._max_chunk_size > self._min_chunk_size:
            if recursive_text_splitter is not None:
                self._recursive_splitter = recursive_text_splitter
            else:
                self._recursive_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=int(self._max_chunk_size),
                    chunk_overlap=int(self._overlap or 0),
                )

    def chunk(self, documents: Iterable[Document]) -> list[Document]:
        """Split documents into chunks.

        The documents are first processed by the semantic chunker,
        and then any oversized chunks are re-split using the recursive text splitter,
        if `self._recursive_splitter` and `self._min_chunk_size`/`self._max_chunk_size` are configured.

        Parameters
        ----------
        documents : Iterable[Document]
            Documents to be chunked.

        Returns
        -------
        list[Document]
            Chunked documents.
        """
        documents_list = list(documents)
        if not documents_list:
            return []

        sem_chunks = self._semantic_chunker.split_documents(documents_list)

        # If no max/min enforcement requested, return directly
        if not self._recursive_splitter:
            return sem_chunks

        # Enforce max size by re-splitting only oversized chunks, then ensure minimum size
        final_chunks: list[Document] = []
        for chunk in sem_chunks:
            text = chunk.page_content or ""
            if len(text) <= self._max_chunk_size:  # type: ignore[arg-type]
                final_chunks.append(chunk)
                continue

            # Split this oversized chunk using the recursive splitter, preserving metadata
            sub_chunks = self._recursive_splitter.split_documents([chunk])  # type: ignore[union-attr]

            # Ensure minimum size by balancing the last small chunk with its predecessor
            balanced = self._rebalance_min_size(sub_chunks)
            final_chunks.extend(balanced)

        return final_chunks

    def _rebalance_min_size(self, chunks: list[Document]) -> list[Document]:
        """Rebalance chunks so that the trailing chunk meets ``min_chunk_size`` when possible.

        Strategy
        --------
        - If the last chunk is smaller than ``min_chunk_size`` and there is a previous chunk,
          combine both and re-split into one or two chunks such that each is within
          [min_chunk_size, max_chunk_size]. This guarantees no tiny tail when feasible.
        - Otherwise, return the chunks unchanged.
        """
        if not chunks or len(chunks) == 1:
            return chunks

        last = chunks[-1]
        prev = chunks[-2]

        overlap = int(self._overlap or 0)
        prev_text = prev.page_content
        last_text = last.page_content
        tail = last_text[overlap:] if overlap > 0 else last_text
        combined_text = prev_text + "\n" + tail
        combined_len = len(combined_text)

        # Case 1: Combined fits entirely under max -> single merged chunk
        if combined_len <= self._max_chunk_size:
            merged = Document(page_content=combined_text, metadata=prev.metadata)
            return chunks[:-2] + [merged]

        # Case 2: Split combined into two parts within [min, max] using sentence boundaries if possible
        # Compute candidate breakpoints at sentence ends
        boundaries = self._sentence_boundaries(combined_text)
        # Ideal target for the first part: stay within [min,max] and leave >= min for the tail
        target_first = combined_len - self._min_chunk_size
        target_first = max(self._min_chunk_size, min(target_first, self._max_chunk_size))

        # Filter boundaries that satisfy constraints for both parts
        valid = self._filter_boundaries(boundaries, combined_len)

        cut_at = None
        if valid:
            # choose boundary closest to target_first
            cut_at = min(valid, key=lambda i: abs(i - target_first))
        else:
            # As a conservative fallback, try any boundary <= max that leaves a non-empty tail
            candidates = [i for i in boundaries if i <= self._max_chunk_size and combined_len - i > 0]
            if candidates:
                cut_at = max(candidates)

        if cut_at is None:
            # Could not find a safe sentence boundary; keep original chunks
            return chunks

        first_text = combined_text[:cut_at]
        second_text = combined_text[cut_at:]
        first = Document(page_content=first_text, metadata=prev.metadata)
        second = Document(page_content=second_text, metadata=prev.metadata)
        return chunks[:-2] + [first, second]

    def _filter_boundaries(self, boundaries: list[int], combined_len: int) -> list[int]:
        """Filter boundaries to find valid split points."""
        valid = []
        for idx in boundaries:
            size1 = idx
            size2 = combined_len - idx
            if size1 < self._min_chunk_size or size1 > self._max_chunk_size:
                continue
            if size2 < self._min_chunk_size:  # leave at least min for the tail
                continue
            valid.append(idx)
        return valid

    def _sentence_boundaries(self, text: str) -> list[int]:
        """Return indices in ``text`` that are good sentence breakpoints.

        Tries NLTK's sentence tokenizer if available, otherwise uses a regex-based
        heuristic to detect sentence ends. Indices are character offsets suitable
        for slicing ``text[:idx]`` and ``text[idx:]``.
        """
        try:
            tokenizer = PunktSentenceTokenizer()
            spans = list(tokenizer.span_tokenize(text))
            return [end for (_, end) in spans]
        except Exception:
            logger.info("NLTK Punkt tokenizer unavailable, falling back to regex-based sentence boundary detection.")
        # Regex heuristic: sentence end punctuation followed by whitespace/newline
        boundaries: list[int] = []
        for m in re.finditer(r"(?<=[\.!?])[\"'”)]*\s+", text):
            boundaries.append(m.end())
        # Ensure we don't return 0 or len(text) as boundaries
        return [i for i in boundaries if 0 < i < len(text)]


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
