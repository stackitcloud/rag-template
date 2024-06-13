from dependency_injector.containers import copy, DeclarativeContainer
from dependency_injector.providers import Singleton
from rag_core.dependency_container import DependencyContainer

from example_replacement_chat_chain import ExampleReplacementChatChain


class UseCaseContainer(DeclarativeContainer):
    chat_chain = Singleton(ExampleReplacementChatChain)
