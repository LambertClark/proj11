from pydantic import BaseModel

class RecordBase(BaseModel):
    name: str
    value: float
    status: str

class RecordCreate(RecordBase):
    pass

class RecordUpdate(RecordBase):
    pass

class RecordOut(RecordBase):
    id: int

    class Config:
        orm_mode = True
