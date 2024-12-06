"""Module for providing no secret provider."""

from rag_core_lib.secret_provider.secret_provider import SecretProvider


class NoSecretProvider(SecretProvider):
    """A secret provider that does not provide any secrets.

    This class is a placeholder implementation of the SecretProvider interface
    that returns empty values for the provided key and token.
    """

    @property
    def provided_key(self) -> str:
        """
        Return an empty string as the provided key.

        Returns
        -------
        str
            An empty string.
        """
        return ""

    def provide_token(self) -> dict:
        """
        Provide an API token.

        Returns
        -------
        dict
            An empty dictionary representing the API token.
        """
        return {}
