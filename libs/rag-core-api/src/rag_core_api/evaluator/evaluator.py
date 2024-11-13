from abc import ABC, abstractmethod


class Evaluator(ABC):
    @abstractmethod
    async def aevaluate() -> None:
        ...
