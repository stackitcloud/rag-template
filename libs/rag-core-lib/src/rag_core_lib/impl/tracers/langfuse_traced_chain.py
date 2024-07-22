from typing import Optional
from langfuse.callback import CallbackHandler
from langchain_core.runnables import RunnableConfig, Runnable

from rag_core_lib.tracers.traced_chain import TracedChain
from rag_core_lib.impl.settings.langfuse_settings import LangfuseSettings


class LangfuseTracedChain(TracedChain):

    CONFIG_CALLBACK_KEY = "callbacks"

    def __init__(self, inner_chain: Runnable, settings: LangfuseSettings):
        super().__init__(inner_chain)
        self._settings = settings

    def _add_tracing_callback(self, session_id: str, config: Optional[RunnableConfig]) -> RunnableConfig:
        handler = CallbackHandler(
            public_key=self._settings.public_key,
            secret_key=self._settings.secret_key,
            host=self._settings.host,
            session_id=session_id,
        )
        if not config:
            return RunnableConfig(callbacks=[handler])

        current_callbacks = config.get(self.CONFIG_CALLBACK_KEY, [])
        config[self.CONFIG_CALLBACK_KEY] = (current_callbacks if current_callbacks else []) + [handler]
        return config
