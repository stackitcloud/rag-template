"""Module for LLM-based answer helpfulness evaluation chain."""

from typing import Any, Optional

from langchain_core.runnables import Runnable, RunnableConfig
from pydantic import BaseModel
from rag_core_lib.runnables.async_runnable import AsyncRunnable
from rag_core_lib.impl.langfuse_manager.langfuse_manager import LangfuseManager


class EvaluationChain(AsyncRunnable[dict, bool]):
    """Simple LLM-based evaluator that returns True if the answer is helpful, else False."""

    def __init__(self, langfuse_manager: LangfuseManager):
        self._langfuse_manager = langfuse_manager

    async def ainvoke(self, chain_input: dict, config: Optional[RunnableConfig] = None, **kwargs: Any) -> bool:
        verdict = await self._create_chain().ainvoke(chain_input, config=config)
        # verdict is a Pydantic model or dict with a boolean field 'helpful'
        try:
            if isinstance(verdict, dict):
                return bool(verdict.get("helpful", False))
            return bool(getattr(verdict, "helpful", False))
        except Exception:
            return False

    def _create_chain(self) -> Runnable:
        prompt = self._langfuse_manager.get_base_prompt(self.__class__.__name__)
        llm = self._langfuse_manager.get_base_llm(self.__class__.__name__)

        class EvaluationVerdict(BaseModel):
            helpful: bool

        # Force structured output using Pydantic schema
        return prompt | llm.with_structured_output(EvaluationVerdict)
