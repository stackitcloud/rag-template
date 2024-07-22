from rag_core_lib.secret_provider.secret_provider import SecretProvider


class NoSecretProvider(SecretProvider):
    @property
    def provided_key(self) -> str:
        return ""

    def provide_token(self) -> dict:
        """Provides an API token."""
        return {}
