from asyncio import gather
from typing import Optional

from langchain_core.runnables import (
    RunnableConfig,
    ensure_config,
)

from admin_api_lib.information_enhancer.information_enhancer import (
    InformationEnhancer,
    RetrieverInput,
    RetrieverOutput,
)


class GeneralEnhancer(InformationEnhancer):
    def __init__(self, enhancers: list[InformationEnhancer]):
        super().__init__()
        self._enhancers = enhancers

    async def ainvoke(self, information: RetrieverInput, config: Optional[RunnableConfig] = None) -> RetrieverOutput:
        config = ensure_config(config)
        summarize_tasks = [enhancer.ainvoke(information, config) for enhancer in self._enhancers]
        summary_results = await gather(*summarize_tasks)
        for summaries in summary_results:
            information += summaries
        return information
