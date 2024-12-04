"""Module for ConfluenceLoader abstract base class."""
from abc import ABC, abstractmethod


class ConfluenceLoader(ABC):
    """Abstract base class for the confluence loader endpoint."""

    @abstractmethod
    async def aload_from_confluence(self) -> None:
        """Load from confluence"""
        pass
