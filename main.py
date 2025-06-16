from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel
import models, schemas
from database import SessionLocal, engine, Base
from routers.crud_router import router

# 初始化数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(router)

# 获取数据库会话
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/records/", response_model=schemas.RecordOut)
def create_record(record: schemas.RecordCreate, db: Session = Depends(get_db_session)):
    db_record = models.Record(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@app.get("/records/", response_model=list[schemas.RecordOut])
def read_records(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    return db.query(models.Record).offset(skip).limit(limit).all()

@app.get("/records/{record_id}", response_model=schemas.RecordOut)
def read_record(record_id: int, db: Session = Depends(get_db_session)):
    record = db.query(models.Record).filter(models.Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@app.put("/records/{record_id}", response_model=schemas.RecordOut)
def update_record(record_id: int, updated: schemas.RecordUpdate, db: Session = Depends(get_db_session)):
    record = db.query(models.Record).filter(models.Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    for k, v in updated.dict().items():
        setattr(record, k, v)
    db.commit()
    db.refresh(record)
    return record

@app.delete("/records/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db_session)):
    record = db.query(models.Record).filter(models.Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()
    return {"message": "Deleted"}

@app.post("/execute_sql")
def execute_sql(payload: dict, db: Session = Depends(get_db_session)):
    sql = payload.get("sql")
    try:
        db.execute(text(sql))
        db.commit()
        return {"success": True, "message": "SQL executed"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    
@app.post("/records/", response_model=schemas.StandardResponse)
def create_record_enhanced(record: schemas.RecordCreate, db: Session = Depends(get_db_session)):
    try:
        db_record = models.Record(**record.dict())
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "记录添加成功",
                "data": {
                    "id": db_record.id,
                    "name": db_record.name,
                    "value": db_record.value,
                    "status": db_record.status
                }
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"添加记录失败：{str(e)}",
                "data": None
            }
        )
    
# SQL请求体的数据结构
class SQLRequest(BaseModel):
    sql: str

# SQL执行接口
@app.post("/exec_sql")
async def exec_sql(sql_req: SQLRequest):
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql_req.sql))
            # 提交事务（如有需要）
            conn.commit()
            return {
                "success": True,
                "message": "SQL executed successfully",
                "rowcount": result.rowcount
            }
    except SQLAlchemyError as e:
        return {
            "success": False,
            "error": str(e.__dict__.get("orig") or str(e))
        }