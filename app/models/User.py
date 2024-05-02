from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, DateTime,Numeric
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT
from sqlalchemy.orm import relationship
from typing import List

from database.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True,nullable=False,autoincrement=True)
    name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    scopes = Column(String(255), nullable=True)
    disabled = Column(Boolean, nullable=True)
    remember_token = Column(String(255), nullable=True)
    last_login_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)    

    sale = relationship("Sale", back_populates="user")

    # @property
    # def discos(self) -> List[Disc]:
    #     discos = []
    #     for venta in self.sale:
    #         discos.append(venta.disc)
    #     return discos
