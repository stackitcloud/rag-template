"""Module for the LangfuseTraceChain class."""

from typing import Optional

from langchain_core.runnables import Runnable, RunnableConfig
from langfuse.langchain import CallbackHandler

from rag_core_lib.impl.settings.langfuse_settings import LangfuseSettings
from rag_core_lib.tracers.traced_runnable import TracedRunnable


class LangfuseTracedRunnable(TracedRunnable):
    """A class to trace the execution of a Runnable using Langfuse.

    This class wraps an inner Runnable and adds tracing capabilities using the Langfuse tracer.
    It allows for the configuration of the tracer through the provided settings.

    Attributes
    ----------
    CONFIG_CALLBACK_KEY : str
        The key used to store callbacks in the configuration.
    """

    CONFIG_CALLBACK_KEY = "callbacks"

    def __init__(self, inner_chain: Runnable, settings: LangfuseSettings):
        """
        Initialize the LangfuseTracedChain with the given inner chain and settings.

        Parameters
        ----------
        inner_chain : Runnable
            The inner chain to be wrapped by this tracer.
        settings : LangfuseSettings
            The settings to configure the Langfuse tracer.
        """
        super().__init__(inner_chain)
        self._settings = settings

    def _add_tracing_callback(self, config: Optional[RunnableConfig]) -> RunnableConfig:
        handler = CallbackHandler(
            public_key=self._settings.public_key,
        )
        if not config:
            return RunnableConfig(callbacks=[handler])

        current_callbacks = config.get(self.CONFIG_CALLBACK_KEY, [])
        config[self.CONFIG_CALLBACK_KEY] = (current_callbacks if current_callbacks else []) + [handler]
        return config
