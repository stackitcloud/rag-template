"""Module containing the Embedder abstract base class."""

from abc import ABC, abstractmethod


class Embedder(ABC):
    """Abstract base class for an embedder."""

    @abstractmethod
    def get_embedder(self) -> "Embedder":
        """Return an instance of the embedder itself."""
