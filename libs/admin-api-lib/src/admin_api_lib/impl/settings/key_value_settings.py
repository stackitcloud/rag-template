"""Contains settings regarding the key values store."""

from pydantic import Field
from pydantic_settings import BaseSettings


class KeyValueSettings(BaseSettings):
    """
    Contains settings regarding the key value store.

    Attributes
    ----------
    host : str
        The hostname of the key value store.
    port : int
        The port number of the key value store.
    username : str | None
        Optional username for authenticating with the key value store.
    password : str | None
        Optional password for authenticating with the key value store.
    use_ssl : bool
        Whether to use SSL/TLS when connecting to the key value store.
    ssl_cert_reqs : str | None
        SSL certificate requirement level (e.g., 'required', 'optional', 'none').
    ssl_ca_certs : str | None
        Path to a CA bundle file for verifying the server certificate.
    ssl_certfile : str | None
        Path to the client SSL certificate file (if mutual TLS is required).
    ssl_keyfile : str | None
        Path to the client SSL private key file (if mutual TLS is required).
    ssl_check_hostname : bool
        Whether to verify the server hostname against the certificate.
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "USECASE_KEYVALUE_"
        case_sensitive = False

    host: str = Field()
    port: int = Field()
    username: str | None = Field(default=None)
    password: str | None = Field(default=None)
    use_ssl: bool = Field(default=False)
    ssl_cert_reqs: str | None = Field(default=None)
    ssl_ca_certs: str | None = Field(default=None)
    ssl_certfile: str | None = Field(default=None)
    ssl_keyfile: str | None = Field(default=None)
    ssl_check_hostname: bool = Field(default=True)
