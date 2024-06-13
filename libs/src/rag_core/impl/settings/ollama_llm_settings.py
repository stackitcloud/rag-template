"""Contains settings regarding the llm.
NOTE: if the title of a field is provided, the field will be configurable in the langfuse UI
      the field names should match the names of the attributes in the corresponding llm class!
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class OllamaSettings(BaseSettings):
    """Contains settings regarding the llm."""

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "OLLAMA_"
        case_sensitive = False

    model: str = Field(default="llama3:instruct")
    base_url: str = Field(default="http://ollama:11434")

    top_k: int = Field(default=0, title="LLM Top K")
    top_p: float = Field(default=0, title="LLM Top P")
    temperature: float = Field(default=0, title="LLM Temperature")
