from pydantic import BaseModel


class RephrasingChainInputData(BaseModel):
    class Config:
        orm_mode = True

    question: str
    history: str
