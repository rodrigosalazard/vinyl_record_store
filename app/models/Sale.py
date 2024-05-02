from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, DateTime,Numeric
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT
from sqlalchemy.orm import relationship
from typing import List

from database.connection import Base

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True,nullable=False,autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    disc_id = Column(Integer, ForeignKey("discs.id"))

    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    user = relationship("User")
    disc = relationship("Disc")
