"""Module containing the dependency injection container for managing application dependencies."""

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton
from fastmcp import FastMCP

from settings.backend_settings import BackendSettings
from settings.mcp_settings import MCPSettings
from rag_mcp_server import RagMcpServer
from rag_backend_client.openapi_client.api.rag_api import RagApi
from rag_backend_client.openapi_client.api_client import ApiClient
from rag_backend_client.openapi_client.configuration import Configuration


class DependencyContainer(DeclarativeContainer):
    """Dependency injection container for managing application dependencies."""

    # Settings
    backend_settings = BackendSettings()
    mcp_settings = MCPSettings()

    api_configuration = Singleton(Configuration, host=backend_settings.base_path)
    api_client = Singleton(ApiClient, configuration=api_configuration)
    rag_api_client = Singleton(RagApi, api_client)

    # Create FastMCP server with just the name - host and port are handled in run()
    mcp_server = Singleton(FastMCP, name=mcp_settings.name)
    rag_mcp_server = Singleton(RagMcpServer, rag_api_client, mcp_server, mcp_settings)
