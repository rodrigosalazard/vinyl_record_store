from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, DateTime,Numeric
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT
from sqlalchemy.orm import relationship
from typing import List

from database.connection import Base

class Disc(Base):
    __tablename__ = "discs"

    id = Column(Integer, primary_key=True, index=True,nullable=False,autoincrement=True)
    file_id = Column(Integer, ForeignKey("files.id"),nullable=True)
    album = Column(String(255), nullable=True)
    artist = Column(String(255), nullable=True)
    genre = Column(String(255), nullable=True)
    year = Column(Integer, nullable=True)
    price = Column(Numeric(10,2), nullable=True)

    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    file = relationship("File")

    sale = relationship("Sale", back_populates="disc")

    @property
    def cover_picture(self):
        if self.file:
            return self.file.file_path
        else:
            return None