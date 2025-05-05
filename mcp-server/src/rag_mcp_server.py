import json
import logging

from mcp.server.fastmcp import FastMCP
from mcp import types

from rag_backend_client.openapi_client.models.chat_request import ChatRequest
from rag_backend_client.openapi_client.api.rag_api import RagApi 

logger = logging.getLogger(__name__)

class RagMcpServer:
    """MCP Server that connects to the RAG backend."""

    def __init__(self, api_client: RagApi, mcp_server: FastMCP, name: str, description: str):
        self._api_client = api_client
        self._server = mcp_server

        self._server.add_tool(
            name=name,
            fn=self._handle_chat,
            description=description,
        )

    async def _handle_chat(self, session_id: str, chat_request: ChatRequest) -> types.CallToolResult:        
        response = self._api_client.chat(session_id, chat_request)
        return types.CallToolResult(content=[types.TextContent(type="text", text=response.to_json())])

    def start(self):
        logger.info(f"Starting MCP Server.")
        self._server.run(transport="sse")
