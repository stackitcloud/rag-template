"""Module for DefaultInformationPiecesRemover class."""

import json
import logging

from fastapi import HTTPException, status

from rag_core_api.api_endpoints.information_piece_remover import InformationPieceRemover
from rag_core_api.models.delete_request import DeleteRequest
from rag_core_api.vector_databases.vector_database import VectorDatabase

logger = logging.getLogger(__name__)


class DefaultInformationPiecesRemover(InformationPieceRemover):
    """DefaultInformationPiecesRemover is responsible for removing information pieces from a vector database."""

    def __init__(self, vector_database: VectorDatabase):
        """Initialize the DefaultInformationPiecesRemover with a vector database.

        Parameters
        ----------
        vector_database : VectorDatabase
            An instance of the VectorDatabase class used for managing vector data.
        """
        self._vector_database = vector_database

    def remove_information_piece(self, delete_request: DeleteRequest) -> None:
        """
        Remove information pieces based on the given delete request.

        Parameters
        ----------
        delete_request : DeleteRequest
            The request object containing the details of the information pieces to be deleted.

        Raises
        ------
        HTTPException
            If there is an error while parsing metadata or deleting from the vector database.

        Returns
        -------
        None
        """
        logger.info("Deleting the information pieces from vector database")
        try:
            metadata = {}
            for key_value_pair in delete_request.metadata:
                metadata["metadata." + key_value_pair.key] = json.loads(key_value_pair.value)
        except Exception:
            logger.exception("Error while parsing metadata")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error while parsing metadata.",
            )
        if not metadata:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No search parameters found.",
            )
        try:
            self._vector_database.delete(metadata)
        except Exception:
            logger.exception("Error while deleting from vector db")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Error while deleting from vector db.",
            )
