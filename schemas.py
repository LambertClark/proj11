from pydantic import BaseModel
from typing import Optional, Any

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
        from_attributes = True

class StandardResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
