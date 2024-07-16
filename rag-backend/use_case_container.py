from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton

from example_replacement_chat_chain import ExampleReplacementChatChain


class UseCaseContainer(DeclarativeContainer):
    chat_chain = Singleton(ExampleReplacementChatChain)
