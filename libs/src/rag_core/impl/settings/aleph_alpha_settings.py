"""Contains settings regarding the aleph_alpha llm.
NOTE: if the title of a field is provided, the field will be configurable in the langfuse UI
      the field names should match the names of the attributes in the corresponding llm class!
"""

from pydantic import Field

from rag_core.impl.settings.llm_settings import LLMSettings


class AlephAlphaSettings(LLMSettings):
    """Contains settings regarding the aleph_alpha llm."""

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "ALEPH_ALPHA_"
        case_sensitive = False

    # concerning authentication
    #   when utilizing the public API
    aleph_alpha_api_key: str = Field(default="", title="aleph alpha api key")
