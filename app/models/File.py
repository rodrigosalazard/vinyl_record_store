from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, DateTime,Numeric
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT
from sqlalchemy.orm import relationship
from typing import List

from database.connection import Base


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True,nullable=False,autoincrement=True)
    file_type = Column(String(255), nullable=True)
    file_name = Column(String(255), nullable=True)
    file_size = Column(String(255), nullable=True)
    file_path = Column(String(255), nullable=True)
    file_extension = Column(String(255), nullable=True)

    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True) 

    disc = relationship("Disc", back_populates="file")
