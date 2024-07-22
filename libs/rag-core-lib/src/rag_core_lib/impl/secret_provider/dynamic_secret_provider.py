"""Manages authentication token via OAuth2."""

import logging
import time
from datetime import datetime

from oauthlib.oauth2 import (
    BackendApplicationClient,
    InvalidClientError,
    InsecureTransportError,
)
from requests_oauthlib import OAuth2Session

from rag_core_lib.impl.secret_provider.authentication_error import AuthenticationError
from rag_core_lib.secret_provider.secret_provider import SecretProvider
from rag_core_lib.impl.settings.stackit_myapi_llm_settings import StackitMyAPILLMSettings


logger = logging.getLogger(__name__)


class DynamicSecretProvider(SecretProvider):
    """Fetch, cache and provide API token."""

    def __init__(self, settings: StackitMyAPILLMSettings) -> None:
        """Fetch, cache and provide API token.

        Parameters
        ----------
        settings : AlephAlphaSettings
            Settings for AlephAlpha
        """
        self._auth_server_url = settings.auth_server_url
        self._auth_client_id = settings.auth_client_id
        self._auth_client_secret = settings.auth_client_secret
        self._token_lifetime_margin = settings.token_lifetime_margin

        self._token_expires_at_time_stamp = time.time()  # assume the none token is already expired
        self._token = None
        self._token_payload = {"grant_type": "client_credentials"}

    @property
    def provided_key(self) -> str:
        return "aleph_alpha_api_key"

    def provide_token(self) -> dict:
        """Provides an authentication token.

        Returns
        -------
        str
            The authentication token.
        """
        if (self._token is None) or (self._token_expires_at_time_stamp < time.time()):
            token = self._generate_new_token()
        else:
            logger.debug("Using cached bearer token.")
            token = self._token
        return {self.provided_key: token}

    def _generate_new_token(self) -> str:
        logger.debug(f"Generating a new token at {self._auth_server_url}.")

        oauth = OAuth2Session(client=BackendApplicationClient(client_id=self._auth_client_id))
        try:
            token = oauth.fetch_token(token_url=self._auth_server_url, client_secret=self._auth_client_secret)
        except InvalidClientError as e:
            logger.error(f"Failed to obtain bearer token: {e}")
            raise AuthenticationError("OAuth2 credentials are not valid.")
        except InsecureTransportError as e:
            logger.error(f"Failed to obtain bearer token: {e}")
            raise AuthenticationError("OAuth2 server url must utilize https")
        except ConnectionError as e:
            logger.error(f"Failed to obtain bearer token: {e}")
            raise AuthenticationError("No connection to authentication server possible.")
        except Exception as e:
            logger.error(f"Failed to obtain bearer token: {e}")
            raise AuthenticationError("Failed to obtain bearer token due to unexpected errors.")

        self._token = token["access_token"]
        self._token_expires_at_time_stamp = token["expires_at"]

        token_lifetime = datetime.fromtimestamp(self._token_expires_at_time_stamp)
        logger.debug(
            f"Successfully acquired an access token from {self._auth_server_url}. "
            f"The token expires at {token_lifetime}."
        )
        self._token_expires_at_time_stamp -= self._token_lifetime_margin  # apply safety margin

        return self._token
