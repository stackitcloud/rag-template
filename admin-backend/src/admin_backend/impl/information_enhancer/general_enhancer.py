from typing import Optional

from langchain_core.runnables import (
    RunnableConfig,
    ensure_config,
)

from admin_backend.information_enhancer.information_enhancer import (
    InformationEnhancer,
    RetrieverInput,
    RetrieverOutput,
)


class GeneralEnhancer(InformationEnhancer):
    def __init__(self, enhancers: list[InformationEnhancer]):
        super().__init__()
        self._enhancers = enhancers

    def invoke(self, information: RetrieverInput, config: Optional[RunnableConfig] = None) -> RetrieverOutput:
        config = ensure_config(config)
        for enhancer in self._enhancers:
            information = enhancer.invoke(information, config)
        return information
