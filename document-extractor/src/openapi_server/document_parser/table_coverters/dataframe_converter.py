from abc import ABC, abstractmethod

import pandas as pd


class DataframeConverter(ABC):
    @staticmethod
    @abstractmethod
    def convert(df: pd.DataFrame) -> str: ...

    @staticmethod
    @abstractmethod
    def convert2df(text: str) -> pd.DataFrame: ...
