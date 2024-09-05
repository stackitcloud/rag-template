from typing import Any

from pydantic import BaseModel


class AnswerChainInputData(BaseModel):
    class Config:
        orm_mode = True

    question: str
    history: str
    retrieved_documents: list[Any]  # TODO: this should be a langchain document
