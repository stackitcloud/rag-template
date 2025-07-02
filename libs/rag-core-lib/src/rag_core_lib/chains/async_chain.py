"""Module for the base class of asynchronous chains."""

from abc import ABC, abstractmethod
from typing import Any, Optional

from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.runnables.utils import Input, Output


class AsyncChain(Runnable[Input, Output], ABC):
    """Base class for asynchronous chains."""

    @abstractmethod
    async def ainvoke(self, chain_input: Input, config: Optional[RunnableConfig] = None, **kwargs: Any) -> Output:
        """Asynchronously invoke the chain with the given input and configuration.

        Parameters
        ----------
        chain_input : Input
            The input data required to asynchronously invoke the chain.
        config : Optional[RunnableConfig], optional
            The configuration settings for the chain invocation, by default None.
        **kwargs : Any
            Additional keyword arguments that may be required for the chain invocation.

        Returns
        -------
        Output
            The result of the chain invocation.
        """

    def invoke(self, chain_input: Input, config: Optional[RunnableConfig] = None, **kwargs: Any) -> Output:
        """
        Invoke the chain with the given input and configuration.

            Typing indicates `Output` will be the return, but because no implementation is planned,
            this will never be returned. This method is not implemented and will raise a not implemented error.

        Notes
        -----
        This method should never be called. It exists only because the base class requires an implementation.

        Parameters
        ----------
        chain_input : Input
            The input data required to invoke the chain.
        config : Optional[RunnableConfig], optional
            The configuration settings for the chain invocation, by default None.

        Returns
        -------
        Output
            The result of the chain invocation.

        Raises
        ------
        NotImplementedError
            Is not implemented, so will raise not implemented error.
        """
        raise NotImplementedError("Please use the async implementation.")
