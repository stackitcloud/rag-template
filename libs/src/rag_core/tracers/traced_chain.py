from abc import ABC, abstractmethod
from typing import Any, Optional

from langchain_core.runnables import (
    Runnable,
    RunnableConfig,
    ensure_config,
)


RunnableInput = Any
RunnableOutput = Any


class TracedChain(Runnable[RunnableInput, RunnableOutput], ABC):

    def __init__(self, inner_chain: Runnable):
        self._inner_chain = inner_chain

    def _get_session_id(self, config: Optional[RunnableConfig]) -> str:
        return config.get("session_id", "None")

    @abstractmethod
    def _add_tracing_callback(self, session_id: str, config: Optional[RunnableConfig]) -> RunnableConfig: ...

    def invoke(self, input: RunnableInput, config: Optional[RunnableConfig] = None, **kwargs: Any) -> RunnableOutput:
        config = ensure_config(config)
        session_id = self._get_session_id(config)
        config_with_tracing = self._add_tracing_callback(session_id, config)
        return self._inner_chain.invoke(input, config=config_with_tracing)
