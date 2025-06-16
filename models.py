from sqlalchemy import Column, Integer, String, Float
from database import Base

class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    value = Column(Float)
    status = Column(String)
