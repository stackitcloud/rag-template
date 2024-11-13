from abc import ABC, abstractmethod
from typing import Any, Optional

from langchain_core.runnables.utils import Input, Output
from langchain_core.runnables import Runnable, RunnableConfig


class AsyncChain(Runnable[Input, Output], ABC):
    """
    Base class for LLM answer generation chain.
    """

    @abstractmethod
    async def ainvoke(self, chain_input: Input, config: Optional[RunnableConfig] = None, **kwargs: Any) -> Output:
        ...

    def invoke(self, chain_input: Input, config: Optional[RunnableConfig] = None, **kwargs: Any) -> Output:
        raise NotImplementedError("Please use the async implementation.")
