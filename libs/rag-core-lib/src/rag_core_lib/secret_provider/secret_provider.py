"""Interface for providing API tokens."""

from abc import ABC, abstractmethod


class SecretProvider(ABC):
    """Interface for providing API tokens."""

    @property
    @abstractmethod
    def provided_key(self) -> str:
        """
        Abstract property that should be implemented to provide a secret key.

        Returns
        -------
        str
            The secret key provided by the implementing class.
        """

    @abstractmethod
    def provide_token(self) -> dict:
        """
        Abstract method that should be implemented to provide an API token.

        Returns
        -------
        dict
            A dictionary containing the API token.
        """
