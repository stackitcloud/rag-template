"""Provide static token provider."""

from rag_core_lib.impl.settings.stackit_vllm_settings import StackitVllmSettings
from rag_core_lib.secret_provider.secret_provider import SecretProvider


class StaticSecretProviderStackit(SecretProvider):
    """Simple API token provider."""

    def __init__(self, settings: StackitVllmSettings):
        """Simple API token provider.

        Parameters
        ----------
        settings : StackitVllmSettings
            Settings for Stackit Vllm service
        """
        self._api_key = settings.api_key

    @property
    def provided_key(self) -> str:
        return "openai_api_key"

    def provide_token(self) -> dict:
        return {self.provided_key: self._api_key}
