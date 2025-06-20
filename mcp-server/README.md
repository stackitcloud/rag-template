# MCP Server

The MCP Server is a Model Context Protocol (MCP) server that provides a bridge between MCP-compatible clients and the RAG backend. It enables AI assistants and other tools to interact with the RAG system through standardized MCP tools.

## Features 🚀

- **Simple Chat Interface**: Basic question-answering without conversation history
- **Chat with History**: Conversational interface that maintains context across messages
- **Citation Support**: Returns source documents and metadata for transparency
- **Streamable HTTP Transport**: Uses HTTP-based transport for reliable communication
- **Configurable Settings**: Environment-based configuration for different deployment scenarios

## Architecture

The server consists of several key components:

- **RagMcpServer**: Main server class that handles MCP tool registration and request routing
- **Dependency Container**: Manages dependency injection for clean architecture
- **Settings**: Environment-based configuration management
- **RAG Backend Client**: Auto-generated OpenAPI client for backend communication

## Requirements

All required python libraries can be found in the [pyproject.toml](pyproject.toml) file.
The MCP server uses Poetry for dependency management and shares the base Dockerfile pattern with other services in the RAG template.

## Available Tools

The server exposes two main MCP tools for interacting with the RAG system:

### `chat_simple`

Simple question-answering interface that returns plain text responses.

**Parameters:**

- `session_id` (str): Unique identifier for the chat session
- `message` (str): The question or message to send to the RAG system

**Returns:**

- `str`: Plain text answer from the RAG system

### `chat_with_history`

Advanced chat interface that supports conversation history and returns structured responses with citations.

**Parameters:**

- `session_id` (str): Unique identifier for the chat session
- `message` (str): The current question or message
- `history` (list[dict], optional): Previous conversation history

**History Format:**
Each history item should be a dictionary with:

- `role`: Either "user" or "assistant"
- `message`: The message content

**Returns:**

- `dict`: Structured response containing:
  - `answer`: The response text
  - `finish_reason`: Why the response ended
  - `citations`: List of source documents with content and metadata

## Configuration

The server supports configuration through environment variables with the following prefixes:

### MCP Settings (`MCP_` prefix)

- `MCP_HOST`: Server bind address (default: `0.0.0.0`)
- `MCP_PORT`: Server port (default: `8000`)
- `MCP_NAME`: Server name (default: `RAG MCP server`)

### Backend Settings (`BACKEND_` prefix)

- `BACKEND_BASE_PATH`: RAG backend URL (default: `http://127.0.0.1:8080`)

## Deployment

The MCP server is designed to be deployed alongside the main RAG backend as a sidecar container. A detailed explanation of the deployment can be found in the [main README](../README.md) and the [infrastructure README](../rag-infrastructure/README.md) of the project.

### Docker Support

The server includes Docker support for containerized deployment and is integrated into the main Tilt development workflow.

### Integration in RAG Template

The MCP server is automatically deployed when `backend.mcp.enabled=true` is set in the Helm values. It runs as a sidecar container alongside the main RAG backend, accessible via:

- **Port**: 8000 (configurable via `MCP_PORT`)
- **Endpoint**: `/mcp` path through the main ingress
- **Development**: Port-forwarded to 9090 in local Tilt setup

## Development

The MCP server is integrated into the main RAG template development workflow:

- **Tilt Integration**: Automatically built and deployed with live reload
- **Linting**: Included in the main linting pipeline
- **Testing**: Part of the overall test suite
- **Debugging**: Supports the same debugging workflow as other services

For detailed development setup instructions, see the [main README](../README.md).
