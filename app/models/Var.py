from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, DateTime,Numeric
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT
from sqlalchemy.orm import relationship
from typing import List

from database.connection import Base
  
class Var(Base):
    __tablename__ = "vars"

    id = Column(Integer, primary_key=True, index=True,nullable=False,autoincrement=True)
    name = Column(String(255), nullable=True)
    value = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    service = Column(String(255), nullable=True)
    status = Column(String(255), nullable=True)

    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
