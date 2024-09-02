import pandas as pd

from openapi_server.document_parser.table_coverters.dataframe_converter import (
    DataframeConverter,
)


class DataFrame2Markdown(DataframeConverter):
    ROW_OFFSET = 2
    COL_OFFSET = 1

    @staticmethod
    def convert(df: pd.DataFrame) -> str:
        text = df.to_markdown()
        text_cells = text.split("|")
        text_cells = [text_cell.strip(" ") for text_cell in text_cells]
        return "|".join(text_cells)

    @staticmethod
    def convert2df(text: str) -> pd.DataFrame:
        data = [
            row.strip("|").split("|")[DataFrame2Markdown.COL_OFFSET :]
            for row in text.split("\n")[DataFrame2Markdown.ROW_OFFSET :]
        ]
        return pd.DataFrame(data)
