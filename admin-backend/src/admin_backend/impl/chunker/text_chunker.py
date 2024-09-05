from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from admin_backend.impl.chunker.chunker import Chunker


class TextChunker(Chunker):
    """
    A class that chunks text documents into smaller chunks.

    Args:
        max_size (int): The maximum size of each chunk.
        overlap (int): The overlap between consecutive chunks.

    Attributes:
        _splitter (RecursiveCharacterTextSplitter): The splitter used for chunking.

    """

    def __init__(self, splitter: RecursiveCharacterTextSplitter):
        # NOTE:  `CharacterTextSplitter` does not take chunk_size into consideration
        #       See: https://github.com/langchain-ai/langchain/issues/10410#issuecomment-1712595675
        #       for that reason, we use the recursive splitter
        self._splitter = splitter

    def chunk(self, documents: Document) -> list[Document]:
        """
        Chunk the given documents into smaller chunks.

        Args:
            documents (Document): The documents to be chunked.

        Returns:
            List[Document]: The list of chunked documents.

        """
        return self._splitter.split_documents(documents)
