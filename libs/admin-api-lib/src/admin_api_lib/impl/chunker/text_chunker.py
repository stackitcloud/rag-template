"""Module containing the TextChunker class."""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from admin_api_lib.chunker.chunker import Chunker


class TextChunker(Chunker):
    """A class that chunks text documents into smaller chunks."""

    def __init__(self, splitter: RecursiveCharacterTextSplitter):
        # NOTE:  `CharacterTextSplitter` does not take chunk_size into consideration
        #       See: https://github.com/langchain-ai/langchain/issues/10410#issuecomment-1712595675
        #       for that reason, we use the recursive splitter
        self._splitter = splitter

    def chunk(self, documents: list[Document]) -> list[Document]:
        """
        Chunk the given documents into smaller chunks.

        Parameters
        ----------
        documents : list[Document]
            The documents to be chunked.

        Returns
        -------
        list[Document]
            The list of chunked documents.

        """
        return self._splitter.split_documents(documents)
