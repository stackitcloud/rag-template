from langchain_core.documents import Document
from langchain_core.embeddings.fake import FakeEmbeddings

from admin_api_lib.impl.chunker.semantic_text_chunker import SemanticTextChunker


def test_semantic_chunker_passes_supported_configuration():
    captured: dict[str, object] = {}

    class RecordingSemanticChunker:
        def __init__(
            self,
            *,
            embeddings,
            breakpoint_threshold_type,
            breakpoint_threshold,
            buffer_size,
            min_chunk_size,
            max_chunk_size,
            trim_chunks,
        ):
            captured.update(
                {
                    "embeddings": embeddings,
                    "breakpoint_threshold_type": breakpoint_threshold_type,
                    "breakpoint_threshold": breakpoint_threshold,
                    "buffer_size": buffer_size,
                    "min_chunk_size": min_chunk_size,
                    "max_chunk_size": max_chunk_size,
                    "trim_chunks": trim_chunks,
                }
            )

        def split_documents(self, documents):
            captured["documents"] = documents
            return [Document(page_content="chunk", metadata={"chunk_index": 0})]

    embeddings = FakeEmbeddings(size=8)
    chunker = SemanticTextChunker(
        embeddings=embeddings,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold=42.0,
        buffer_size=3,
        min_chunk_size=120,
        max_chunk_size=480,
        trim_chunks=False,
        chunker_cls=RecordingSemanticChunker,
    )

    docs = [Document(page_content="content", metadata={"id": "a"})]
    chunks = chunker.chunk(docs)

    assert captured["embeddings"] is embeddings
    assert captured["breakpoint_threshold_type"] == "percentile"
    assert captured["breakpoint_threshold"] == 42.0
    assert captured["buffer_size"] == 3
    assert captured["min_chunk_size"] == 120
    assert captured["max_chunk_size"] == 480
    assert captured["trim_chunks"] is False
    assert captured["documents"] == docs
    assert chunks[0].page_content == "chunk"


def test_semantic_chunker_ignores_unsupported_kwargs():
    created: dict[str, object] = {}

    class MinimalSemanticChunker:
        def __init__(self, embeddings):
            created["embeddings"] = embeddings

        def split_documents(self, documents):
            created["documents"] = documents
            return documents

    embeddings = FakeEmbeddings(size=4)
    chunker = SemanticTextChunker(
        embeddings=embeddings,
        breakpoint_threshold=12.0,
        buffer_size=2,
        min_chunk_size=50,
        max_chunk_size=400,
        chunker_cls=MinimalSemanticChunker,
    )

    docs = [Document(page_content="hola mundo")]
    result = chunker.chunk(docs)

    assert created["embeddings"] is embeddings
    assert created["documents"] == docs
    assert result == docs


def test_semantic_chunker_returns_empty_list_for_no_documents():
    embeddings = FakeEmbeddings(size=2)
    chunker = SemanticTextChunker(embeddings=embeddings)

    assert chunker.chunk([]) == []
