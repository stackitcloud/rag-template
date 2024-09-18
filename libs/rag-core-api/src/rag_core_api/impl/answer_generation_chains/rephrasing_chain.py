from abc import ABC
from typing import Any, Optional

from langchain_core.runnables import Runnable, RunnableConfig


from rag_core_lib.chains.async_chain import AsyncChain
from rag_core_lib.impl.langfuse_manager.langfuse_manager import LangfuseManager

from rag_core_api.impl.answer_generation_chains.rephrasing_chain_input_data import (
    RephrasingChainInputData,
)

RunnableInput = RephrasingChainInputData
RunnableOutput = str


class RephrasingChain(AsyncChain[RunnableInput, RunnableOutput], ABC):
    """
    Base class for rephrasing of the input question.
    """

    def __init__(self, langfuse_manager: LangfuseManager):
        self._langfuse_manager = langfuse_manager

    async def ainvoke(
        self, chain_input: RunnableInput, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> RunnableOutput:
        prompt_input = chain_input.model_dump()
        return await self._create_chain().ainvoke(prompt_input, config=config)

    def _create_chain(self) -> Runnable:
        return self._langfuse_manager.get_base_prompt(self.__class__.__name__) | self._langfuse_manager.get_base_llm(
            self.__class__.__name__
        )
