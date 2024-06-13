from typing import Optional
from langfuse.callback import CallbackHandler
from langchain_core.runnables import RunnableConfig, Runnable

from rag_core.tracers.traced_chain import TracedChain
from rag_core.impl.settings.langfuse_settings import LangfuseSettings


class LangfuseTracedChain(TracedChain):

    def __init__(self, inner_chain: Runnable, settings: LangfuseSettings):
        super().__init__(inner_chain)
        self._settings = settings

    def _add_tracing_callback(self, session_id: str, config: Optional[RunnableConfig]) -> RunnableConfig:
        self._settings = LangfuseSettings()  # TODO: no idea why the injected settings are broken
        handler = CallbackHandler(
            public_key=self._settings.public_key,
            secret_key=self._settings.secret_key,
            host=self._settings.host,
            session_id=session_id,
        )  # TODO: find out how to create an object with DI at calltime with the session id already set
        if not config:
            return RunnableConfig(callbacks=[handler])

        config["callbacks"] = (config["callbacks"] if "callbacks" in config.keys() and config["callbacks"] else []) + [
            handler
        ]
        return config
