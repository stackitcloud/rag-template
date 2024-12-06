"""Provide static token provider."""

from rag_core_lib.impl.settings.aleph_alpha_settings import AlephAlphaSettings
from rag_core_lib.secret_provider.secret_provider import SecretProvider


class StaticSecretProviderAlephAlpha(SecretProvider):
    """Simple API token provider."""

    def __init__(self, settings: AlephAlphaSettings):
        """Initialize the StaticSecretProviderAlephAlpha.

        Parameters
        ----------
        settings : AlephAlphaSettings
            Settings for AlephAlpha
        """
        self._api_key = settings.aleph_alpha_api_key

    @property
    def provided_key(self) -> str:
        """
        Property that provides a hard coded key for Aleph Alpha API.

        Returns
        -------
        str
            The provided key for Aleph Alpha API.
        """
        return "aleph_alpha_api_key"

    def provide_token(self) -> dict:
        """
        Provide a token as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the provided key and the API key.
        """
        return {self.provided_key: self._api_key}
