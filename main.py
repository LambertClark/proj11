from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import SessionLocal, engine, Base

# 初始化数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/records/", response_model=schemas.RecordOut)
def create_record(record: schemas.RecordCreate, db: Session = Depends(get_db)):
    db_record = models.Record(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@app.get("/records/", response_model=list[schemas.RecordOut])
def read_records(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Record).offset(skip).limit(limit).all()

@app.get("/records/{record_id}", response_model=schemas.RecordOut)
def read_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(models.Record).filter(models.Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@app.put("/records/{record_id}", response_model=schemas.RecordOut)
def update_record(record_id: int, updated: schemas.RecordUpdate, db: Session = Depends(get_db)):
    record = db.query(models.Record).filter(models.Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    for k, v in updated.dict().items():
        setattr(record, k, v)
    db.commit()
    db.refresh(record)
    return record

@app.delete("/records/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(models.Record).filter(models.Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()
    return {"message": "Deleted"}