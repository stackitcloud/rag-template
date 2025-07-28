"""Module for the LangchainDocument2InformationPiece class."""

from extractor_api_lib.mapper.source_langchain_document2information_piece import (
    SourceLangchainDocument2InformationPiece,
)


class LangchainDocument2InformationPiece(SourceLangchainDocument2InformationPiece):
    """A class to map a LangchainDocument to an InformationPiece."""

    def _map_meta(self, internal: dict, document_name: str) -> dict:
        return internal
