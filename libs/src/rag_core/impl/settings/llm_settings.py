"""Contains settings regarding the llm.
NOTE: if the title of a field is provided, the field will be configurable in the langfuse UI
      the field names should match the names of the attributes in the corresponding llm class!
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class LLMSettings(BaseSettings):
    """Contains settings regarding the llm."""

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "LLM_"
        case_sensitive = False

    # concerning authentication
    #   when utilizing the public API
    model: str = Field(default="luminous-supreme-control-20240215")
    host: str = Field(default="https://api.aleph-alpha.com")

    top_k: int = Field(default=0, title="LLM Top K")
    top_p: float = Field(default=0, title="LLM Top P")
    presence_penalty: float = Field(default=0, title="LLM Presence Penalty")
    frequency_penalty: float = Field(default=0, title="LLM Frequency Penalty")
    maximum_tokens: int = Field(default=150, title="LLM maximum tokens")
    temperature: float = Field(default=0, title="LLM Temperature")
    sequence_penalty: float = Field(default=0, title="LLM Sequence Penalty")
    repetition_penalties_include_prompt: bool = Field(default=False, title="LLM repetition Penalties Include Prompt")
    repetition_penalties_include_completion: bool = Field(
        default=True, title="LLM repetition Penalties Include Completion"
    )
    best_of: int = Field(default=2, title="LLM Best Of")
    n: int = Field(default=1, title="LLM N")
    stop_sequences: list[str] = Field(default=["Q:", "Response:"], title="LLM Stop Sequences")
