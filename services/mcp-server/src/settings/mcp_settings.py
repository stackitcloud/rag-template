"""Module that contains settings for the MCP server."""

from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Dict

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

    # Chat Simple Method Configuration
    chat_simple_description: str = Field(
        default="Send a message to the RAG system and get a simple text response.\n\nThis is the simplest way to interact with the RAG system - just provide a message and get back the answer as plain text."
    )
    chat_simple_parameter_descriptions: Dict[str, str] = Field(
        default_factory=lambda: {
            "session_id": "Unique identifier for the chat session.",
            "message": "The message/question to ask the RAG system."
        }
    )
    chat_simple_returns: str = Field(
        default="The answer from the RAG system as plain text."
    )
    chat_simple_notes: str = Field(default="")
    chat_simple_examples: str = Field(default="")

    # Chat With History Method Configuration
    chat_with_history_description: str = Field(
        default="Send a message with conversation history and get structured response.\n\nProvide conversation history as a simple list of dictionaries.\nEach history item should have 'role' (either 'user' or 'assistant') and 'message' keys."
    )
    chat_with_history_parameter_descriptions: Dict[str, str] = Field(
        default_factory=lambda: {
            "session_id": "Unique identifier for the chat session.",
            "message": "The current message/question to ask.",
            "history": "Previous conversation history. Each item should be:\n    {\"role\": \"user\" or \"assistant\", \"message\": \"the message text\"}"
        }
    )
    chat_with_history_returns: str = Field(
        default="Response containing:\n    - answer: The response text\n    - finish_reason: Why the response ended\n    - citations: List of source documents used (simplified)"
    )
    chat_with_history_notes: str = Field(default="")
    chat_with_history_examples: str = Field(default="")
