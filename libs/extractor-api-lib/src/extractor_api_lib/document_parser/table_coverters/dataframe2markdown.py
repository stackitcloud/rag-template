import pandas as pd

from extractor_api_lib.document_parser.table_coverters.dataframe_converter import (
    DataframeConverter,
)


class DataFrame2Markdown(DataframeConverter):
    ROW_OFFSET = 2
    COL_OFFSET = 1

    def convert(self, df: pd.DataFrame) -> str:
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
