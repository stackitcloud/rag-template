"""Module containing the Embedder abstract base class."""

from abc import ABC, abstractmethod


class Embedder(ABC):
    """
    Abstract base class for an embedder.

    This class defines the interface for an embedder, which is responsible for
    generating embeddings for given inputs.
    """

    @abstractmethod
    def get_embedder(self) -> "Embedder":
        """
        Abstract method to get an instance of the Embedder class itself.

        Returns
        -------
        Embedder
            An instance of the Embedder class itself.
        """
