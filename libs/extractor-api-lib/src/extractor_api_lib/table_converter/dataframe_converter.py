"""Module containing the DataFrameConverter abstract class."""

from abc import ABC, abstractmethod

import pandas as pd


class DataframeConverter(ABC):
    """Abstract base class for converting between pandas DataFrames and their string representations.

    This class defines the interface for converting a pandas DataFrame to a string and vice versa.
    Subclasses must implement the `convert` and `convert2df` methods.
    """

    @abstractmethod
    def convert(self, df: pd.DataFrame) -> str:
        """
        Convert a pandas DataFrame to a string representation.

        Parameters
        ----------
        df : pd.DataFrame
            The DataFrame to be converted.

        Returns
        -------
        str
            The string representation of the DataFrame.
        """

    @abstractmethod
    def convert2df(self, text: str) -> pd.DataFrame:
        """
        Convert the given text to a pandas DataFrame.

        Parameters
        ----------
        text : str
            The text to be converted into a DataFrame.

        Returns
        -------
        pd.DataFrame
            The resulting DataFrame after conversion.
        """
