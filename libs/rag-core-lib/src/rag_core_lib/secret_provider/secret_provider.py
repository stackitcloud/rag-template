"""Interface for providing API tokens."""

from abc import ABC, abstractmethod


class SecretProvider(ABC):
    """Interface for providing API tokens."""

    @property
    @abstractmethod
    def provided_key(self) -> str:
        ...

    @abstractmethod
    def provide_token(self) -> dict:
        """Provides an API token."""
