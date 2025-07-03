"""Module for converting a pandas DataFrame to a Markdown string representation."""

import pandas as pd

from extractor_api_lib.table_converter.dataframe_converter import DataframeConverter


class DataFrame2Markdown(DataframeConverter):
    """A class to convert pandas DataFrames to Markdown string representations and vice versa.

    Attributes
    ROW_OFFSET : int
        The number of rows to skip when converting from markdown to DataFrame.
    COL_OFFSET : int
        The number of columns to skip when converting from markdown to DataFrame.
    """

    ROW_OFFSET = 2
    COL_OFFSET = 1

    def convert(self, df: pd.DataFrame) -> str:
        """
        Convert a pandas DataFrame to a Markdown string representation.

            The Markdown string representation of the DataFrame.

        Parameters
        ----------
        df : pd.DataFrame
            The DataFrame to be converted.

        Returns
        -------
        str
            The Markdown string representation of the DataFrame.
        """
        table_df = self._drop_empty_rows(df)
        if df.empty:
            return ""
        table_df = self._replace_cariage_returns(table_df)
        table_df = self._replace_new_lines(table_df)
        table_df.replace(pd.NA, "", inplace=True)
        text = table_df.to_markdown()
        text_cells = text.split("|")
        text_cells = [text_cell.strip(" ") for text_cell in text_cells]
        return "|".join(text_cells)

    def convert2df(self, text: str) -> pd.DataFrame:
        """
        Convert the given markdown table text to a pandas DataFrame.

        Parameters
        ----------
        text : str
            The markdown table text to be converted into a DataFrame. Each row should be separated
            by a newline character, and columns should be separated by the '|' character.

        Returns
        -------
        pd.DataFrame
            The resulting DataFrame after conversion, with each cell containing the corresponding
            text from the markdown table.
        """
        data = [
            row.strip("|").split("|")[DataFrame2Markdown.COL_OFFSET :]
            for row in text.split("\n")[DataFrame2Markdown.ROW_OFFSET :]
        ]
        return pd.DataFrame(data)

    def _replace_cariage_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.replace(r"\r", " ", regex=True)

    def _replace_new_lines(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.replace(r"\n", " ", regex=True)

    def _drop_empty_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        df.replace("", pd.NA, inplace=True)
        df = df.dropna(axis=0, how="all")

        return df.dropna(axis=1, how="all")
