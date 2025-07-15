"""Module that contains settings regarding langfuse."""

from pydantic import Field
from pydantic_settings import BaseSettings


class RagasSettings(BaseSettings):
    """
    Contains settings regarding ragas.

    Attributes
    ----------
    use_openai : bool
        Flag to indicate whether to use OpenAI services (default True).
    model : str
        The model name to be used (default "gpt-4o-mini").
    openai_api_key : str
        The API key for accessing OpenAI services (default empty string).
    timeout : int
        The timeout duration in seconds for API requests (default 60).
    evaluation_dataset_name : str
        The name of the evaluation dataset (default "eval-data").
    dataset_filename : str
        The filename of the dataset (default "test_data.json").
    max_concurrency : int
        The maximum number of concurrent requests (default 5).
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "RAGAS_"
        case_sensitive = False

    use_openai: bool = Field(default=True)
    model: str = Field(default="gpt-4o-mini")
    openai_api_key: str = Field(default="")
    timeout: int = Field(default=60)
    evaluation_dataset_name: str = Field(default="eval-data")
    dataset_filename: str = Field(default="test_data.json")
    max_concurrency: int = Field(default=5)
