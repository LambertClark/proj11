from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter()

# 模拟数据库（内存）
fake_db = []

class Record(BaseModel):
    id: int
    name: str
    value: float
    status: str

@router.post("/records", response_model=Record)
def create_record(record: Record):
    fake_db.append(record)
    return record

@router.get("/records", response_model=List[Record])
def get_all_records():
    return fake_db

@router.get("/records/{record_id}", response_model=Record)
def get_record(record_id: int):
    for rec in fake_db:
        if rec.id == record_id:
            return rec
    raise HTTPException(status_code=404, detail="Record not found")

@router.put("/records/{record_id}", response_model=Record)
def update_record(record_id: int, updated: Record):
    for i, rec in enumerate(fake_db):
        if rec.id == record_id:
            fake_db[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Record not found")

@router.delete("/records/{record_id}")
def delete_record(record_id: int):
    for i, rec in enumerate(fake_db):
        if rec.id == record_id:
            del fake_db[i]
            return {"detail": "Deleted"}
    raise HTTPException(status_code=404, detail="Record not found")
