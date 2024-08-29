from typing import Any, List

from pydantic import BaseModel


class AnswerChainInputData(BaseModel):
    class Config:
        orm_mode = True

    question: str
    history: str
    retrieved_documents: List[Any]  # TODO: this should be a langchain document
