"""Module for configuring and initializing the MCP server."""

import logging

from fastmcp import FastMCP
from pydantic_settings import BaseSettings

from rag_backend_client.openapi_client.models.chat_request import ChatRequest
from rag_backend_client.openapi_client.api.rag_api import RagApi
from rag_backend_client.openapi_client.models.chat_response import ChatResponse
from rag_backend_client.openapi_client.models.chat_history import ChatHistory
from rag_backend_client.openapi_client.models.chat_history_message import ChatHistoryMessage
from rag_backend_client.openapi_client.models.chat_role import ChatRole
from typing import Any

from docstring_system import DocstringTemplateSystem, extensible_docstring, setup_extensible_docstrings

logger = logging.getLogger(__name__)


class RagMcpServer:
    """MCP Server that connects to the RAG backend."""

    TRANSPORT = "streamable-http"

    def __init__(self, api_client: RagApi, mcp_server: FastMCP, settings: BaseSettings):
        self._api_client = api_client
        self._server = mcp_server
        self._settings = settings

        # Initialize the docstring system
        docstring_system = DocstringTemplateSystem(settings)
        setup_extensible_docstrings(self, docstring_system)

        self._register_tools()

    def run(self):
        """Run the MCP server with specified transport."""
        logger.info(
            "Starting FastMCP Server on %s://%s:%s",
            self.TRANSPORT,
            self._settings.host,
            self._settings.port,
        )
        self._server.run(transport=self.TRANSPORT, host=self._settings.host, port=self._settings.port)

    @extensible_docstring("chat_simple")
    async def chat_simple(self, session_id: str, message: str) -> str:
        chat_request = ChatRequest(message=message)
        response = await self._handle_chat(session_id, chat_request)
        return response.answer

    @extensible_docstring("chat_with_history")
    async def chat_with_history(
        self, session_id: str, message: str, history: list[dict[str, str]] = None
    ) -> dict[str, Any]:
        # Build chat history if provided
        chat_history = None
        if history:
            history_messages = []
            for item in history:
                role = ChatRole.USER if item.get("role", "").lower() == "user" else ChatRole.ASSISTANT
                history_messages.append(ChatHistoryMessage(role=role, message=item["message"]))
            chat_history = ChatHistory(messages=history_messages)

        chat_request = ChatRequest(message=message, history=chat_history)
        response = await self._handle_chat(session_id, chat_request)

        # Simplify citations for easier consumption
        simplified_citations = []
        for citation in response.citations:
            simplified_citations.append(
                {"content": citation.page_content, "metadata": {pair.key: pair.value for pair in citation.metadata}}
            )

        return {"answer": response.answer, "finish_reason": response.finish_reason, "citations": simplified_citations}

    def _register_tools(self):
        """Register all MCP tools with the server."""
        # Simple tools for basic agent usage
        self._server.add_tool(self._server.tool(self.chat_simple))
        self._server.add_tool(self._server.tool(self.chat_with_history))

    async def _handle_chat(self, session_id: str, chat_request: ChatRequest) -> ChatResponse:
        """Handle the chat request with the RAG backend."""
        try:
            return self._api_client.chat(session_id, chat_request)

        except Exception as e:
            logger.exception("Error in chat request")
            raise Exception(f"Failed to process chat request: {str(e)}")
