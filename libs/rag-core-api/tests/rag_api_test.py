"""Test module for the RAG core API."""

import os
import json
from typing import AsyncGenerator
import uuid
from sys import maxsize

from httpx import ASGITransport, AsyncClient, Response
import pytest
import pytest_asyncio
from fastapi import FastAPI
from dependency_injector import providers
from qdrant_client import QdrantClient
from qdrant_client.http import models

from mock_environment_variables import mock_environment_variables
from mock_logging_directory import mock_logging_config

mock_environment_variables()
mock_logging_config()

from rag_core_api.main import app
from rag_core_api.models.chat_request import ChatRequest
from rag_core_api.models.chat_history import ChatHistory
from rag_core_api.models.chat_history_message import ChatHistoryMessage
from rag_core_api.models.chat_role import ChatRole
from rag_core_api.models.information_piece import InformationPiece
from rag_core_api.models.content_type import ContentType
from rag_core_api.models.key_value_pair import KeyValuePair
from rag_core_api.models.delete_request import DeleteRequest
from rag_core_api.impl.settings.fake_embedder_settings import FakeEmbedderSettings
from rag_core_api.impl.settings.error_messages import ErrorMessages


@pytest_asyncio.fixture
async def adjusted_app() -> AsyncGenerator[FastAPI, None]:
    """
    Fixture that provides asynchronously an adjusted FastAPI application with an in-memory Qdrant vector database.

    Yields
    -------
    FastAPI
        The application instance with the in-memory vector database configured.
    """
    collection_name = os.environ.get("VECTOR_DB_COLLECTION_NAME")
    with app.container.vectordb_client.override(
        providers.Singleton(QdrantClient, os.environ.get("VECTOR_DB_LOCATION"))
    ):
        client = app.container.vectordb_client()
        if not client.collection_exists(collection_name):
            client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=FakeEmbedderSettings().size, distance=models.Distance.COSINE),
            )
        yield app
        # Clean up
        app.container.vector_database()._vectorstore.client.delete_collection(collection_name)


@pytest_asyncio.fixture
async def api_client(adjusted_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that asynchronously creates an async test client for FastAPI application testing.

    Parameters
    ----------
    adjusted_app : FastAPI
        The FastAPI application instance with adjusted settings for testing.

    Yields
    -------
    AsyncClient
        An asynchronous HTTP client configured to interact with the test server.
    """
    base_url = "http://testserver"
    async with AsyncClient(base_url=base_url, transport=ASGITransport(app=adjusted_app), timeout=10.0) as client:
        yield client


def _create_information_pieces() -> list[dict]:
    return [
        InformationPiece(
            page_content="The capital of Germany is Berlin.",
            type=ContentType.TEXT,
            metadata=[
                KeyValuePair(key="document_url", value=json.dumps("http://example.com/mydoc1.xml")).model_dump(),
                KeyValuePair(key="type", value=json.dumps("TEXT")).model_dump(),
                KeyValuePair(key="related", value=json.dumps([])).model_dump(),
                KeyValuePair(key="id", value=json.dumps(uuid.uuid4().hex)).model_dump(),
            ],
        ).model_dump(),
        InformationPiece(
            page_content="The Eiffel Tower is located in Paris, France.",
            type=ContentType.TEXT,
            metadata=[
                KeyValuePair(key="document_url", value=json.dumps("http://example.com/eiffel_tower.xml")).model_dump(),
                KeyValuePair(key="type", value=json.dumps("TEXT")).model_dump(),
                KeyValuePair(key="related", value=json.dumps([])).model_dump(),
                KeyValuePair(key="id", value=json.dumps(uuid.uuid4().hex)).model_dump(),
            ],
        ).model_dump(),
        InformationPiece(
            page_content="Mount Everest is the highest mountain in the world.",
            type=ContentType.TEXT,
            metadata=[
                KeyValuePair(key="document_url", value=json.dumps("http://example.com/mount_everest.xml")).model_dump(),
                KeyValuePair(key="type", value=json.dumps("TEXT")).model_dump(),
                KeyValuePair(key="related", value=json.dumps([])).model_dump(),
                KeyValuePair(key="id", value=json.dumps(uuid.uuid4().hex)).model_dump(),
            ],
        ).model_dump(),
        InformationPiece(
            page_content="The Amazon Rainforest produces 20% of the world's oxygen.",
            type=ContentType.TEXT,
            metadata=[
                KeyValuePair(
                    key="document_url", value=json.dumps("http://example.com/amazon_rainforest.xml")
                ).model_dump(),
                KeyValuePair(key="type", value=json.dumps("TEXT")).model_dump(),
                KeyValuePair(key="related", value=json.dumps([])).model_dump(),
                KeyValuePair(key="id", value=json.dumps(uuid.uuid4().hex)).model_dump(),
            ],
        ).model_dump(),
        InformationPiece(
            page_content="The Great Wall of China is over 13,000 miles long.",
            type=ContentType.TEXT,
            metadata=[
                KeyValuePair(key="document_url", value=json.dumps("http://example.com/great_wall.xml")).model_dump(),
                KeyValuePair(key="type", value=json.dumps("TEXT")).model_dump(),
                KeyValuePair(key="related", value=json.dumps([])).model_dump(),
                KeyValuePair(key="id", value=json.dumps(uuid.uuid4().hex)).model_dump(),
            ],
        ).model_dump(),
        InformationPiece(
            page_content="The Sahara Desert is the largest hot desert in the world.",
            type=ContentType.TEXT,
            metadata=[
                KeyValuePair(key="document_url", value=json.dumps("http://example.com/sahara_desert.xml")).model_dump(),
                KeyValuePair(key="type", value=json.dumps("TEXT")).model_dump(),
                KeyValuePair(key="related", value=json.dumps([])).model_dump(),
                KeyValuePair(key="id", value=json.dumps(uuid.uuid4().hex)).model_dump(),
            ],
        ).model_dump(),
        InformationPiece(
            page_content="The Mona Lisa was painted by Leonardo da Vinci.",
            type=ContentType.TEXT,
            metadata=[
                KeyValuePair(key="document_url", value=json.dumps("http://example.com/mona_lisa.xml")).model_dump(),
                KeyValuePair(key="type", value=json.dumps("TEXT")).model_dump(),
                KeyValuePair(key="related", value=json.dumps([])).model_dump(),
                KeyValuePair(key="id", value=json.dumps(uuid.uuid4().hex)).model_dump(),
            ],
        ).model_dump(),
        InformationPiece(
            page_content="The Pacific Ocean is the largest ocean on Earth.",
            type=ContentType.TEXT,
            metadata=[
                KeyValuePair(key="document_url", value=json.dumps("http://example.com/pacific_ocean.xml")).model_dump(),
                KeyValuePair(key="type", value=json.dumps("TEXT")).model_dump(),
                KeyValuePair(key="related", value=json.dumps([])).model_dump(),
                KeyValuePair(key="id", value=json.dumps(uuid.uuid4().hex)).model_dump(),
            ],
        ).model_dump(),
        InformationPiece(
            page_content="The Colosseum is located in Rome, Italy.",
            type=ContentType.TEXT,
            metadata=[
                KeyValuePair(key="document_url", value=json.dumps("http://example.com/colosseum.xml")).model_dump(),
                KeyValuePair(key="type", value=json.dumps("TEXT")).model_dump(),
                KeyValuePair(key="related", value=json.dumps([])).model_dump(),
                KeyValuePair(key="id", value=json.dumps(uuid.uuid4().hex)).model_dump(),
            ],
        ).model_dump(),
        InformationPiece(
            page_content="The speed of light is approximately 299,792 kilometers per second.",
            type=ContentType.TEXT,
            metadata=[
                KeyValuePair(
                    key="document_url", value=json.dumps("http://example.com/speed_of_light.xml")
                ).model_dump(),
                KeyValuePair(key="type", value=json.dumps("TEXT")).model_dump(),
                KeyValuePair(key="related", value=json.dumps([])).model_dump(),
                KeyValuePair(key="id", value=json.dumps(uuid.uuid4().hex)).model_dump(),
            ],
        ).model_dump(),
        InformationPiece(
            page_content="The human brain contains approximately 86 billion neurons.",
            type=ContentType.TEXT,
            metadata=[
                KeyValuePair(key="document_url", value=json.dumps("http://example.com/human_brain.xml")).model_dump(),
                KeyValuePair(key="type", value=json.dumps("TEXT")).model_dump(),
                KeyValuePair(key="related", value=json.dumps([])).model_dump(),
                KeyValuePair(key="id", value=json.dumps(uuid.uuid4().hex)).model_dump(),
            ],
        ).model_dump(),
    ]


def _create_chat_requests() -> list[dict]:
    return [
        ChatRequest(
            message="What is the capital of Germany?",
            chat_history=ChatHistory(
                messages=[
                    ChatHistoryMessage(role=ChatRole.USER, message="How many people live in Berlin?").model_dump()
                ]
            ).model_dump(),
        ).model_dump(),
        ChatRequest(
            message="What is the capital of Germany?",
            chat_history=ChatHistory(
                messages=[
                    ChatHistoryMessage(role=ChatRole.USER, message="How many people live in Berlin?").model_dump(),
                    ChatHistoryMessage(
                        role=ChatRole.ASSISTANT, message="Berlin has a population of about 3.7 million people."
                    ).model_dump(),
                ]
            ).model_dump(),
        ).model_dump(),
        ChatRequest(
            message="What is the capital of Germany?",
            chat_history=ChatHistory(
                messages=[
                    ChatHistoryMessage(role=ChatRole.USER, message="How many people live in Berlin?").model_dump(),
                    ChatHistoryMessage(role=ChatRole.USER, message="And what is the GDP of Berlin?").model_dump(),
                ]
            ).model_dump(),
        ).model_dump(),
        ChatRequest(
            message="What is the capital of Germany?",
            chat_history=ChatHistory(
                messages=[
                    ChatHistoryMessage(role=ChatRole.USER, message="How many people live in Berlin?").model_dump(),
                    ChatHistoryMessage(
                        role=ChatRole.ASSISTANT, message="Berlin has a population of about 3.7 million people."
                    ).model_dump(),
                    ChatHistoryMessage(role=ChatRole.USER, message="What is the GDP of Berlin?").model_dump(),
                ]
            ).model_dump(),
        ).model_dump(),
        ChatRequest(
            message="What is the capital of Germany?",
            chat_history=ChatHistory(
                messages=[
                    ChatHistoryMessage(role=ChatRole.USER, message="How many people live in Berlin?").model_dump(),
                    ChatHistoryMessage(
                        role=ChatRole.ASSISTANT, message="Berlin has a population of about 3.7 million people."
                    ).model_dump(),
                    ChatHistoryMessage(role=ChatRole.USER, message="What is the GDP of Berlin?").model_dump(),
                    ChatHistoryMessage(
                        role=ChatRole.ASSISTANT, message="The GDP of Berlin is approximately €160 billion."
                    ).model_dump(),
                ]
            ).model_dump(),
        ).model_dump(),
        ChatRequest(
            message="What is the capital of Germany?", chat_history=ChatHistory(messages=[]).model_dump()
        ).model_dump(),
    ]


@pytest.mark.asyncio
async def test_chat(api_client: AsyncClient):
    """Test the chat endpoint functionality.

    This test verifies the chat endpoint behavior by uploading information pieces and sending
    chat requests to ensure proper responses.

    Parameters
    ----------
    api_client : AsyncClient
        The test client for making HTTP requests.
    """
    information_pieces = _create_information_pieces()

    response = await api_client.post("/information_pieces/upload", json=information_pieces)
    response.raise_for_status()

    _session_id = "test-session"

    _chat_requests = _create_chat_requests()

    error_messages = ErrorMessages()
    error_messages_list = [
        error_messages.no_documents_message,
        error_messages.no_or_empty_collection,
        error_messages.harmful_question,
        error_messages.no_answer_found,
    ]

    for _chat_request in _chat_requests:
        response = await api_client.post(f"/chat/{_session_id}", json=_chat_request)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data

        error_messages = ErrorMessages()
        assert data["answer"] not in error_messages_list


async def _delete_document(api_client: AsyncClient, metadata: list[dict]) -> Response:
    _delete_request = DeleteRequest(metadata=metadata).model_dump()
    return await api_client.post("/information_pieces/remove", json=_delete_request)


@pytest.mark.asyncio
async def test_delete_document(api_client: AsyncClient):
    """
    Test the document deletion functionality of the API.

    This test verifies both single document deletion by ID and bulk deletion by type.

    Parameters
    ----------
    api_client : AsyncClient
        The API client fixture used for making HTTP requests.

    Raises
    ------
    HTTPError
        If any API request fails
    AssertionError
        If any test assertions fail
    """
    # Upload test information pieces
    information_pieces = _create_information_pieces()
    response = await api_client.post("/information_pieces/upload", json=information_pieces)
    response.raise_for_status()

    # Verify initial upload
    collection_name = os.environ.get("VECTOR_DB_COLLECTION_NAME")
    app_container = api_client._transport.app.container
    vectordb_client = app_container.vector_database()._vectorstore.client
    initial_points = vectordb_client.scroll(collection_name=collection_name, limit=maxsize)[0]
    assert len(initial_points) == len(information_pieces)

    # Test deleting single document by id
    delete_id = information_pieces[-1]["metadata"][-1]["value"]
    response = await _delete_document(api_client, [{"key": "id", "value": delete_id}])
    assert response.status_code == 200
    remaining_points = vectordb_client.scroll(collection_name=collection_name, limit=maxsize)[0]
    assert len(remaining_points) == len(information_pieces) - 1

    # Test bulk deletion by type
    response = await _delete_document(api_client, [{"key": "type", "value": json.dumps("TEXT")}])
    assert response.status_code == 200
    final_points = vectordb_client.scroll(collection_name=collection_name, limit=maxsize)[0]
    assert len(final_points) == 0


@pytest.mark.asyncio
async def test_chat_empty_message(api_client: AsyncClient):
    """Verify the chat endpoint behavior when an empty message is sent."""
    # TODO: this should return an error message, it should be not possible to send an empty message
    information_pieces = _create_information_pieces()

    response = await api_client.post("/information_pieces/upload", json=information_pieces)
    response.raise_for_status()

    _session_id = "test-session"
    _chat_request = ChatRequest(message="", history=ChatHistory(messages=[]).model_dump()).model_dump()

    response = await api_client.post(f"/chat/{_session_id}", json=_chat_request)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    error_messages = ErrorMessages()
    error_messages_list = [
        error_messages.no_documents_message,
        error_messages.no_or_empty_collection,
        error_messages.harmful_question,
        error_messages.no_answer_found,
    ]
    assert data["answer"] not in error_messages_list


@pytest.mark.asyncio
async def test_chat_only_whitespace_character_message(api_client: AsyncClient):
    """Verify the chat endpoint behavior when a message with only whitespace characters is sent.

    Parameters
    ----------
    api_client : AsyncClient
        The API client fixture used for making HTTP requests.
    """
    # TODO: this should return an error message, it should be not possible to send a message
    # with only whitespace characters
    information_pieces = _create_information_pieces()

    response = await api_client.post("/information_pieces/upload", json=information_pieces)
    response.raise_for_status()

    _session_id = "test-session"
    _chat_requests = [
        ChatRequest(message=" ", chat_history=ChatHistory(messages=[]).model_dump()).model_dump(),  # Space
        ChatRequest(message="\t", chat_history=ChatHistory(messages=[]).model_dump()).model_dump(),  # Tab
        ChatRequest(message="\n", chat_history=ChatHistory(messages=[]).model_dump()).model_dump(),  # Newline
        ChatRequest(message="\r", chat_history=ChatHistory(messages=[]).model_dump()).model_dump(),  # Carriage return
        ChatRequest(message="\f", chat_history=ChatHistory(messages=[]).model_dump()).model_dump(),  # Form feed
        ChatRequest(message="\v", chat_history=ChatHistory(messages=[]).model_dump()).model_dump(),  # Vertical tab
        ChatRequest(
            message=" \t\n\r\f\v", chat_history=ChatHistory(messages=[]).model_dump()  # All combined
        ).model_dump(),
    ]

    for _chat_request in _chat_requests:
        response = await api_client.post(f"/chat/{_session_id}", json=_chat_request)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        error_messages = ErrorMessages()
        error_messages_list = [
            error_messages.no_documents_message,
            error_messages.no_or_empty_collection,
            error_messages.harmful_question,
            error_messages.no_answer_found,
        ]
        assert data["answer"] not in error_messages_list


@pytest.mark.asyncio
async def test_chat_without_collection_points(api_client: AsyncClient):
    """Verify the chat endpoint behavior when no documents are uploaded to the collection.

    Parameters
    ----------
    api_client : AsyncClient
        The API client fixture used for making HTTP requests.
    """
    _session_id = "test-session"
    _chat_request = {"message": "What is the capital of Germany?", "chat_history": {"messages": []}}
    response = await api_client.post(f"/chat/{_session_id}", json=_chat_request)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data

    assert data["answer"] == ErrorMessages().no_or_empty_collection


@pytest.mark.asyncio
async def test_chat_with_summary_only_type(api_client: AsyncClient):
    """Verify the chat endpoint behavior when only summary type documents are uploaded.

    Parameters
    ----------
    api_client : AsyncClient
        The API client fixture used for making HTTP requests.
    """
    information_pieces = [
        InformationPiece(
            page_content="The capital of Germany is Berlin.",
            type=ContentType.SUMMARY,
            metadata=[
                KeyValuePair(key="document_url", value=json.dumps("http://localblub/mydoc1.xml")).model_dump(),
                KeyValuePair(key="type", value=json.dumps("SUMMARY")).model_dump(),
                KeyValuePair(key="related", value=json.dumps([])).model_dump(),
                KeyValuePair(key="id", value=json.dumps(uuid.uuid4().hex)).model_dump(),
            ],
        ).model_dump()
    ]

    response = await api_client.post("/information_pieces/upload", json=information_pieces)
    response.raise_for_status()

    _session_id = "test-session"
    _chat_request = {"message": "What is the capital of Germany?", "chat_history": {"messages": []}}

    response = await api_client.post(f"/chat/{_session_id}", json=_chat_request)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data

    assert data["answer"] == ErrorMessages().no_documents_message


@pytest.mark.asyncio
async def test_upload_documents(api_client: AsyncClient):
    """Verify the document upload functionality of the API.

    Parameters
    ----------
    api_client : AsyncClient
        The API client fixture used for making HTTP requests.
    """
    information_pieces = [
        InformationPiece(
            page_content="The capital of Germany is Berlin.",
            type=ContentType.SUMMARY,
            metadata=[
                KeyValuePair(key="document_url", value=json.dumps("http://localblub/mydoc1.xml")).model_dump(),
                KeyValuePair(key="type", value=json.dumps("SUMMARY")).model_dump(),
                KeyValuePair(key="related", value=json.dumps([])).model_dump(),
                KeyValuePair(key="id", value=json.dumps(uuid.uuid4().hex)).model_dump(),
            ],
        ).model_dump()
    ]
    response = await api_client.post("/information_pieces/upload", json=information_pieces)
    response.raise_for_status()

    collection_name = os.environ.get("VECTOR_DB_COLLECTION_NAME")
    app_container = api_client._transport.app.container
    vectordb_client = app_container.vector_database()._vectorstore.client
    number_of_documents = len(vectordb_client.scroll(collection_name=collection_name, limit=maxsize)[0])
    assert number_of_documents == 1

    information_pieces = _create_information_pieces()
    response = await api_client.post("/information_pieces/upload", json=information_pieces)
    app_container = api_client._transport.app.container
    vectordb_client = app_container.vector_database()._vectorstore.client
    number_of_documents = len(vectordb_client.scroll(collection_name=collection_name, limit=maxsize)[0])
    # NOTE: its not asserted to be of length len(information_pieces)+1 because in case of in memory database,
    # overwriting the vectorstore leads to overwriting the contents in the collection.
    assert number_of_documents == len(information_pieces)
