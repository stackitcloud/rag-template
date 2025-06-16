import json
import logging
from typing import Any, Optional

from fastmcp import FastMCP
from pydantic_settings import BaseSettings

from rag_backend_client.openapi_client.models.chat_history import ChatHistory
from rag_backend_client.openapi_client.models.chat_request import ChatRequest
from rag_backend_client.openapi_client.api.rag_api import RagApi

logger = logging.getLogger(__name__)


class RagMcpServer:
    """MCP Server that connects to the RAG backend."""

    TRANSPORT = "streamable-http"

    def __init__(self, api_client: RagApi, mcp_server: FastMCP, settings: BaseSettings):
        self._api_client = api_client
        self._server = mcp_server
        self._settings = settings

        @self._server.tool
        async def chat_with_rag(session_id: str, message: str, history: Optional[ChatHistory] = None) -> dict[str, Any]:
            """Chat with the RAG backend system.

            Parameters
            ----------
            session_id: str
                Unique identifier for the chat session.
            message: str
                The user's message/question.
            history: Optional[ChatHistory]
                Chat history to be used for the conversation.
            """
            return await self._handle_chat(session_id, message, history)

    def run(self):
        """Run the MCP server with specified transport."""
        logger.info(f"Starting FastMCP Server on {self.TRANSPORT}://{self._settings.host}:{self._settings.port}")
        self._server.run(transport=self.TRANSPORT, host=self._settings.host, port=self._settings.port)

    async def _handle_chat(
        self, session_id: str, message: str, history: Optional[ChatHistory] = None
    ) -> dict[str, Any]:
        """Handle the chat request with the RAG backend."""
        try:
            chat_request = ChatRequest(message=message, history=history)

            response = self._api_client.chat(session_id, chat_request)

            if hasattr(response, "to_dict"):
                return response.to_dict()
            elif hasattr(response, "to_json"):
                return json.loads(response.to_json())
            else:
                return {"response": str(response)}

        except Exception as e:
            logger.error(f"Error in chat request: {str(e)}")
            return {"error": f"Failed to process chat request: {str(e)}"}
