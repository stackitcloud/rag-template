"""Module for ConfluenceLoader abstract base class."""
from abc import ABC, abstractmethod


class ConfluenceLoader(ABC):
    """Abstract base class for the confluence loader endpoint."""

    @abstractmethod
    async def aload_from_confluence(self) -> None:
        """
        Load data from Confluence asynchronously.

        This method should be implemented to load data asynchronously from Confluence.

        Returns
        -------
        None
        """
