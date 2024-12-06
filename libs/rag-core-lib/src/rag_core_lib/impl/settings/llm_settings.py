"""Module that contains settings regarding the LLM."""

from pydantic import Field
from pydantic_settings import BaseSettings


class LLMSettings(BaseSettings):
    """
    Contains settings regarding the LLM.

    Attributes
    ----------
    model : str
        The model name to be used.
    host : str
        The host URL for the API.
    top_k : int
        Number of most likely tokens to consider at each step.
    top_p : float
        Total probability mass of tokens to consider at each step.
    presence_penalty : float
        The penalty for presence of a token in the generated text.
    frequency_penalty : float
        The penalty for frequency of a token in the generated text.
    maximum_tokens : int
        The maximum number of tokens to generate.
    temperature : float
        The sampling temperature to use.
    sequence_penalty : float
        The penalty for sequences in the generated text.
    repetition_penalties_include_prompt : bool
        Flag deciding whether presence penalty or frequency penalty are
        updated from the prompt.
    repetition_penalties_include_completion : bool
        Flag deciding whether presence penalty or frequency penalty
        are updated from the completion.
    best_of : int
        The number of completions to generate server-side and return the best.
    n : int
        The number of completions to generate for each prompt.
    stop_sequences : list of str
        The sequences where the model will stop generating further tokens.

    Notes
    -----
    If the title of a field is provided, the field will be configurable in the Langfuse UI.
    The field names should match the names of the attributes in the corresponding llm class.
    """

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
