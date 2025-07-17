"""Module that contains settings for the Fake LLM."""

from pydantic import Field
from pydantic_settings import BaseSettings


class MCPSettings(BaseSettings):
    """
    Settings for the mcp server.

    Attributes
    ----------
    host : str
        The address to bind to.
    port : int
        The port to bind to.
    name : str
        Name of the mcp server.
    tool_name : str
        Name of the mcp tool.
    tool_description : str
        Description of the mcp tool.
    """

    class Config:
        """Configuration for reading fields from the environment."""

        env_prefix = "MCP_"
        case_sensitive = False

    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    name: str = Field(default="RAG MCP server")
    chat_simple_description: str = Field(
        default="""Send a message to the RAG system and get a simple text response.

        This is the simplest way to interact with the RAG system - just provide a message
        and get back the answer as plain text.
        """
    )
    chat_with_history_description: str = Field(
        default="""Send a message with conversation history and get structured response.

        Provide conversation history as a simple list of dictionaries.
        Each history item should have 'role' (either 'user' or 'assistant') and 'message' keys.
        """
    )
