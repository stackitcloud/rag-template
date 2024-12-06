"""Contains settings regarding the aleph_alpha llm."""

from pydantic import Field

from rag_core_lib.impl.settings.llm_settings import LLMSettings


class AlephAlphaSettings(LLMSettings):
    """Contains settings regarding the aleph_alpha llm.

    Attributes
    ----------
    aleph_alpha_api_key : str
        The API key for authenticating with the Aleph Alpha service.

    Notes
    -----
    If the title of a field is provided, the field will be configurable in the Langfuse UI.
    The field names should match the names of the attributes in the corresponding llm class.
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "ALEPH_ALPHA_"
        case_sensitive = False

    # concerning authentication
    #   when utilizing the public API
    aleph_alpha_api_key: str = Field(default="", title="aleph alpha api key")
