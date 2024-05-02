from typing import List, Union, Optional
from fastapi import HTTPException
from pydantic import BaseModel, Field, Required, validator
from datetime import datetime

'''

    USER

'''
class User(BaseModel):
    id: int
    name: Optional[str] = Field(nullable=True)
    username: Optional[str] = Field(nullable=True)
    email: str
    scopes: str

    class Config:
        orm_mode = True

class UserInDB(User):
    password: str


class UserSignIn(BaseModel):
    name: str = None
    username: str = None
    email: str
    password: str = None
    confirm_password: str = None

    @validator('*')
    def check_null(cls, v,field):
        if v is None or v == "":
            raise HTTPException(status_code=404, detail=f"El campo '{field.name}' es obligatorio.")
        return v

class UserCreate(BaseModel):
    name: str = None
    username: str = None
    email: str = None
    password: str = None
    confirm_password: str = None
    scopes: str = None

    @validator('*')
    def check_null(cls, v,field):
        if v is None or v == "":
            raise HTTPException(status_code=404, detail=f"El campo '{field.name}' es obligatorio.")
        return v

class UserUpdate(BaseModel):
    name: str = None
    username: str = None
    email: Optional[str] = None
    password: Optional[str] = None
    confirm_password: Optional[str] = None
    scopes: str = None

    @validator('*')
    def check_null(cls, v,field):
        if v is None or v == "":
            raise HTTPException(status_code=404, detail=f"El campo '{field.name}' es obligatorio.")
        return v

class UserProfile(BaseModel):
    name: str = None
    username: str = None
    password: Optional[str] = None
    confirm_password: Optional[str] = None

    @validator('*')
    def check_null(cls, v,field):
        if v is None:
            raise HTTPException(status_code=404, detail=f"El campo '{field.name}' es obligatorio.")
        return v


class UserBase(BaseModel):
    id: int
    name: str
    username: str
    email: str

    class Config:
        orm_mode = True


class UserDisc(BaseModel):
    id: int
    album: Optional[str] = Field(nullable=True)
    artist: Optional[str] = Field(nullable=True)
    genre: Optional[str] = Field(nullable=True)
    year: Optional[int] = Field(nullable=True)
    price: Optional[float] = Field(nullable=True)
    cover_picture: Optional[str] = Field(nullable=True)
    purchase_date: datetime = None
