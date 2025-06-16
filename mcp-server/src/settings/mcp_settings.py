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
    tool_name:str = Field()
    tool_description:str = Field()
