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
            breakpoint_threshold_amount,
            buffer_size,
            min_chunk_size,
        ):
            captured.update(
                {
                    "embeddings": embeddings,
                    "breakpoint_threshold_type": breakpoint_threshold_type,
                    "breakpoint_threshold_amount": breakpoint_threshold_amount,
                    "buffer_size": buffer_size,
                    "min_chunk_size": min_chunk_size,
                }
            )

        def split_documents(self, documents):
            captured["documents"] = documents
            return [Document(page_content="chunk", metadata={"chunk_index": 0})]

    embeddings = FakeEmbeddings(size=8)
    chunker = SemanticTextChunker(
        embeddings=embeddings,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=42.0,
        buffer_size=3,
        min_chunk_size=120,
        max_chunk_size=480,
        chunker_cls=RecordingSemanticChunker,
    )

    docs = [Document(page_content="content", metadata={"id": "a"})]
    chunks = chunker.chunk(docs)

    assert captured["embeddings"] is embeddings
    assert captured["breakpoint_threshold_type"] == "percentile"
    assert captured["breakpoint_threshold_amount"] == 42.0
    assert captured["buffer_size"] == 3
    assert captured["min_chunk_size"] == 120
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
        breakpoint_threshold_amount=12.0,
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


def test_enforces_max_and_min_chunk_sizes_with_balancing():
    class PassthroughSemanticChunker:
        def __init__(self, *, embeddings, **_):  # accept any extra kwargs
            self._embeddings = embeddings

        def split_documents(self, documents):
            # Return the documents unchanged (so post-processing applies)
            return documents

    embeddings = FakeEmbeddings(size=4)
    max_sz = 300
    min_sz = 200
    long_text = "Once in a valley of copper leaves, a child found a lantern with a whisper inside. It called itself Anemone, a small AI born from starlight and old clocks. “I can learn anything,” it murmured, “if you teach me kindly.” The child taught it lullabies and rivers, riddles and recipes, and Anemone glowed brighter than the moon. One night a storm sliced the valley and the bridge to the village tore away. The child trembled. Anemone listened to the wind, mapped every raindrop, and sang a path across the broken air. The village crossed, candle by candle. “I only borrowed your courage,” said the lantern. “Keep it, then,” said the child, “and keep learning, too.” So they wandered, mending, together. Together they asked questions and when answers thinned, they planted new ones as tiny seeds."
    docs = [Document(page_content=long_text)]

    chunker = SemanticTextChunker(
        embeddings=embeddings,
        min_chunk_size=min_sz,
        max_chunk_size=max_sz,
        chunker_cls=PassthroughSemanticChunker,
    )

    chunks = chunker.chunk(docs)

    # All chunks should be within [min, max]
    lengths = [len(c.page_content) for c in chunks]
    assert all(min_sz <= length <= max_sz for length in lengths)
    # And the total length should match the original (ignoring the single added newline on merge/split bounds)
    summed_length = sum(lengths)
    assert summed_length <= len(long_text) + 1
    assert len(long_text) - 2 <= summed_length


def test_rebalance_merges_when_combined_under_max():
    # min=50, max=100. prev=60, last=20 -> combined=80 <= max, expect single merge
    embeddings = FakeEmbeddings(size=4)
    min_size, max_size = 50, 100
    chunker = SemanticTextChunker(
        embeddings=embeddings,
        min_chunk_size=min_size,
        max_chunk_size=max_size,
        overlap=0,
    )

    prev = Document(page_content=("A" * 60) + ".")
    last = Document(page_content=("B" * 20) + ".")

    out = chunker._rebalance_min_size([prev, last])
    assert len(out) == 1
    merged_len = len(out[0].page_content)
    assert merged_len <= max_size
    assert merged_len >= min_size or merged_len >= 80  # allow exact combined when slightly under min


def test_rebalance_sentence_aware_split_two_parts_within_bounds():
    # min=50, max=100. combined ~ 120, choose boundary to get ~70/50 split
    embeddings = FakeEmbeddings(size=4)
    min_size, max_size = 50, 100
    chunker = SemanticTextChunker(
        embeddings=embeddings,
        min_chunk_size=min_size,
        max_chunk_size=max_size,
        overlap=0,
    )

    # Build prev of ~90 chars in multiple sentences; last ~30
    s1 = ("A" * 35) + "."
    s2 = ("B" * 35) + "."
    s3 = ("C" * 20) + "."
    prev = Document(page_content=" ".join([s1, s2, s3]))
    last = Document(page_content=("D" * 30) + ".")

    combined_len = len(prev.page_content + "\n" + last.page_content)
    out = chunker._rebalance_min_size([prev, last])
    assert len(out) == 2
    len1 = len(out[0].page_content)
    len2 = len(out[1].page_content)

    assert min_size <= len1 <= max_size
    assert len2 >= min_size
    assert len1 + len2 == combined_len
