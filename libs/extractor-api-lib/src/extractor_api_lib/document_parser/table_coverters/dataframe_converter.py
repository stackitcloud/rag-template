from abc import ABC, abstractmethod

import pandas as pd


class DataframeConverter(ABC):
    @abstractmethod
    def convert(self, df: pd.DataFrame) -> str:
        ...

    @abstractmethod
    def convert2df(self, text: str) -> pd.DataFrame:
        ...
