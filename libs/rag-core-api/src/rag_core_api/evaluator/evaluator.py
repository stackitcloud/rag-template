"""Module for the Evaluator class."""

from abc import ABC, abstractmethod


class Evaluator(ABC):
    """Evaluator is responsible for evaluating questions in a dataset using various metrics."""

    @abstractmethod
    async def aevaluate() -> None:
        """Asynchronously evaluates the questions in the evaluation dataset."""
