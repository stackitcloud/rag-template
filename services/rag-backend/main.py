"""Module for the use case main application."""

from rag_core_api.main import app as perfect_rag_app  # noqa: F401
from rag_core_api.main import register_dependency_container

from container import UseCaseContainer

register_dependency_container(UseCaseContainer())
