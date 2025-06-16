import json
import logging
from typing import Dict, Any

from fastmcp import FastMCP
from pydantic_settings import BaseSettings

from rag_backend_client.openapi_client.models.chat_request import ChatRequest
from rag_backend_client.openapi_client.api.rag_api import RagApi

logger = logging.getLogger(__name__)

class RagMcpServer:
    """MCP Server that connects to the RAG backend."""

    def __init__(self, api_client: RagApi, mcp_server: FastMCP, settings: BaseSettings):
        self._api_client = api_client
        self._server = mcp_server
        self._settings = settings

        # Register the chat tool using the new FastMCP decorator pattern
        @self._server.tool
        async def chat_with_rag(session_id: str, message: str, context: str = "") -> Dict[str, Any]:
            """Chat with the RAG backend system.

            Args:
                session_id: Unique identifier for the chat session
                message: The user's message/question
                context: Optional additional context for the conversation

            Returns:
                Dict containing the response from the RAG system
            """
            return await self._handle_chat(session_id, message, context)

    async def _handle_chat(self, session_id: str, message: str, context: str = "") -> Dict[str, Any]:
        """Handle the chat request with the RAG backend."""
        try:
            # Create the chat request object
            chat_request = ChatRequest(message=message, context=context)

            # Call the RAG API
            response = self._api_client.chat(session_id, chat_request)

            # Return the response as a dictionary for better JSON serialization
            if hasattr(response, 'to_dict'):
                return response.to_dict()
            elif hasattr(response, 'to_json'):
                return json.loads(response.to_json())
            else:
                return {"response": str(response)}

        except Exception as e:
            logger.error(f"Error in chat request: {str(e)}")
            return {"error": f"Failed to process chat request: {str(e)}"}

    def run(self, transport: str = "streamable-http"):
        """Run the MCP server with specified transport."""
        logger.info(f"Starting FastMCP Server on {transport}://{self._settings.host}:{self._settings.port}")
        self._server.run(transport=transport, host=self._settings.host, port=self._settings.port)
