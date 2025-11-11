"""Module containing the GeneralEnhancer class."""

from asyncio import gather
from typing import Optional

from langchain_core.runnables import RunnableConfig, ensure_config

from admin_api_lib.information_enhancer.information_enhancer import (
    InformationEnhancer,
    RetrieverInput,
    RetrieverOutput,
)


class GeneralEnhancer(InformationEnhancer):
    """The GeneralEnhancer aggregates multiple InformationEnhancer instances.

    InformationEnhancers are applied asynchronously to the input information.
    """

    def __init__(self, enhancers: list[InformationEnhancer]):
        """Initialize the GeneralEnhancer with a list of InformationEnhancer instances.

        Parameters
        ----------
        enhancers : list of InformationEnhancer
            A list of InformationEnhancer instances to be used by the GeneralEnhancer.
        """
        super().__init__()
        self._enhancers = enhancers

    async def ainvoke(self, information: RetrieverInput, config: Optional[RunnableConfig] = None) -> RetrieverOutput:
        """Asynchronously invokes the each information enhancer with the given input and configuration.

        Parameters
        ----------
        information : RetrieverInput
            The input information to be processed by the general information enhancer.
        config : Optional[RunnableConfig], optional
            The configuration settings for the general information enhancer, by default None.

        Returns
        -------
        RetrieverOutput
            The output after processing the input information.
        """
        config = ensure_config(config)
        summarize_tasks = [enhancer.ainvoke(information, config) for enhancer in self._enhancers]
        summary_results = await gather(*summarize_tasks)
        for summaries in summary_results:
            information += summaries
        return information
