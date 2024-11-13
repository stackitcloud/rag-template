import uuid
from abc import ABC, abstractmethod
from typing import Any, Optional

from langchain_core.runnables import Runnable, RunnableConfig, ensure_config
from rag_core_lib.chains.async_chain import AsyncChain

RunnableInput = Any
RunnableOutput = Any


class TracedGraph(AsyncChain[RunnableInput, RunnableOutput], ABC):
    SESSION_ID_KEY = "session_id"
    METADATA_KEY = "metadata"

    def __init__(self, inner_chain: Runnable):
        self._inner_chain = inner_chain

    async def ainvoke(
        self, chain_input: RunnableInput, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> RunnableOutput:
        config = ensure_config(config)
        session_id = self._get_session_id(config)
        config_with_tracing = self._add_tracing_callback(session_id, config)
        return await self._inner_chain.ainvoke(chain_input, config=config_with_tracing)

    @abstractmethod
    def _add_tracing_callback(self, session_id: str, config: Optional[RunnableConfig]) -> RunnableConfig:
        ...

    def _get_session_id(self, config: Optional[RunnableConfig]) -> str:
        return config.get(self.METADATA_KEY, {}).get(self.SESSION_ID_KEY, str(uuid.uuid4()))
