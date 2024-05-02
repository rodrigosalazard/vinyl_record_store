from typing import List, Union, Optional
from fastapi import HTTPException
from pydantic import BaseModel, Field, Required, validator
from datetime import datetime
from schemas.User import UserBase
from schemas.Disc import Disc

'''

    SALE

'''

class Sale(BaseModel):
    id: int
    user: UserBase
    disc: Disc
    created_at: datetime = None
    updated_at: datetime = None

    class Config:
        orm_mode = True

    def __init__(self, **data):
        super().__init__(**data)
        if self.created_at is not None:
            self.created_at = datetime.strptime(self.created_at, '%Y-%m-%dT%H:%M:%S.%f').strftime('%d/%m/%Y')
        if self.updated_at is not None:
            self.updated_at = datetime.strptime(self.updated_at, '%Y-%m-%dT%H:%M:%S.%f').strftime('%d/%m/%Y')       


class SaleCreate(BaseModel):
    disc_id: int


class SaleDiscUser(BaseModel):
    id: int
    #disc info
    disc_id: int
    album: Optional[str] = Field(nullable=True)
    artist: Optional[str] = Field(nullable=True)
    genre: Optional[str] = Field(nullable=True)
    year: Optional[int] = Field(nullable=True)
    price: Optional[float] = Field(nullable=True)
    cover_picture: Optional[str] = Field(nullable=True)
    purchase_date: datetime = None
    #user info
    user_id: int
    name: str
    username: str
    email: str