"""Module that contains settings regarding the LLM."""

from pydantic import Field
from pydantic_settings import BaseSettings


class OllamaSettings(BaseSettings):
    """
    Contains settings regarding the LLM.

    Attributes
    ----------
    model : str
      The model name to be used.
    base_url : str
      The base URL for the LLM.
    top_k : int
      Reduces the probability of generating nonsense. A higher value (e.g. 100) will give more diverse answers,
      while a lower value (e.g. 10) will be more conservative.
    top_p : float
      Works together with top-k. A higher value (e.g., 0.95) will lead to more diverse text,
      while a lower value (e.g., 0.5) will generate more focused and conservative text.
    temperature : float
      The temperature of the model. Increasing the temperature will make the model answer more creatively.

    Notes
    -----
    If the title of a field is provided, the field will be configurable in the Langfuse UI
    the field names should match the names of the attributes in the corresponding LLM class!
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "OLLAMA_"
        case_sensitive = False

    model: str = Field(default="llama3:instruct")
    base_url: str = Field(default="http://ollama:11434")

    top_k: int = Field(default=0, title="LLM Top K")
    top_p: float = Field(default=0, title="LLM Top P")
    temperature: float = Field(default=0, title="LLM Temperature")
