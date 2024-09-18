from typing import (
    Any,
    Optional,
)

from langchain_core.language_models.llms import LLM
from langchain_core.callbacks import CallbackManagerForLLMRun


from rag_core_lib.secret_provider.secret_provider import SecretProvider


class SecuredLLM(LLM):

    llm: Any
    secret_provider: SecretProvider

    @property
    def _llm_type(self) -> str:
        return self.llm._llm_type  # TODO: is there a better way to do this?

    def _call(
        self,
        prompt: str,
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Run the LLM on the given prompt and input."""
        secrets = self.secret_provider.provide_token()
        return self.llm.with_config({"configurable": secrets}).invoke(prompt, stop, **kwargs)

    async def _acall(
        self,
        prompt: str,
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Run the LLM on the given prompt and input."""
        secrets = self.secret_provider.provide_token()
        return await self.llm.with_config({"configurable": secrets}).ainvoke(prompt, stop, **kwargs)
