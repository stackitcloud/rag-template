"""Provides mock environment variables for testing purposes.

This module contains functions to set up mock environment variables required for
testing the RAG core library. It includes configurations for vector database,
logging, LLM parameters, retriever settings etc.
"""

import os
import tempfile


def mock_environment_variables() -> None:
    """Mock environment variables for testing purposes.

    This function sets up a testing environment by setting various environment variables
    with mock values. It includes configuration for vector database, API keys,
    model parameters, logging, and retrieval settings.
    """
    os.environ["VECTOR_DB_LOCATION"] = ":memory:"
    os.environ["VECTOR_DB_COLLECTION_NAME"] = "test_rag_collection"
    os.environ["LANGFUSE_SECRET_KEY"] = "placeholder"
    os.environ["LANGFUSE_PUBLIC_KEY"] = "placeholder"
    os.environ["LANGFUSE_HOST"] = "http://localhost:8000"
    os.environ["STACKIT_VLLM_MODEL"] = "test_key"
    os.environ["STACKIT_VLLM_BASE_URL"] = "http://localhost:8000"
    os.environ["STACKIT_VLLM_API_KEY"] = "test_key"
    os.environ["STACKIT_VLLM_TOP_P"] = "0.1"  #
    os.environ["STACKIT_VLLM_TEMPERATURE"] = "0"  #
    temp_dir = tempfile.mkdtemp()
    temp_logging_config = os.path.join(temp_dir, "logging.yaml")
    os.environ["LOGGING_DIRECTORY"] = temp_logging_config
    os.environ["EMBEDDER_CLASS_TYPE_EMBEDDER_TYPE"] = "fake"
    os.environ["RAG_CLASS_TYPE_LLM_TYPE"] = "fake"

    os.environ["RETRIEVER_THRESHOLD"] = "0.0"
    os.environ["RETRIEVER_K_DOCUMENTS"] = "10"
    os.environ["RETRIEVER_TOTAL_K"] = "10"
    os.environ["RETRIEVER_TABLE_THRESHOLD"] = "0.0"
    os.environ["RETRIEVER_TABLE_K_DOCUMENTS"] = "10"
    os.environ["RETRIEVER_SUMMARY_THRESHOLD"] = "0.0"
    os.environ["RETRIEVER_SUMMARY_K_DOCUMENTS"] = "10"
    os.environ["RETRIEVER_IMAGE_THRESHOLD"] = "0.0"
    os.environ["RETRIEVER_IMAGE_K_DOCUMENTS"] = "10"
