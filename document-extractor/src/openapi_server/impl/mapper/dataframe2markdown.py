import pandas as pd

from openapi_server.impl.mapper.dataframe_converter import DataframeConverter


class DataFrame2Markdown(DataframeConverter):
    ROW_OFFSET = 2
    COL_OFFSET = 1

    def convert(self, df: pd.DataFrame) -> str:
        text = df.to_markdown()
        text_cells = text.split("|")
        text_cells = [text_cell.strip(" ") for text_cell in text_cells]
        return "|".join(text_cells)

    def convert2df(self, text: str) -> pd.DataFrame:
        data = [row.strip("|").split("|")[self.COL_OFFSET :] for row in text.split("\n")[self.ROW_OFFSET :]]
        return pd.DataFrame(data)
