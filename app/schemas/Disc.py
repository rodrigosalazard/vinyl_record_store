from typing import List, Union, Optional
from fastapi import HTTPException
from pydantic import BaseModel, Field, Required, validator
from datetime import datetime

'''

    DISC

'''
class Disc(BaseModel):
    id: int
    album: Optional[str] = Field(nullable=True)
    artist: Optional[str] = Field(nullable=True)
    genre: Optional[str] = Field(nullable=True)
    year: Optional[int] = Field(nullable=True)
    price: Optional[float] = Field(nullable=True)
    cover_picture: Optional[str] = Field(nullable=True)

    class Config:
        orm_mode = True



class DiscCreate(BaseModel):
    album: str = None
    artist: str = None
    genre: str = None
    year: int = None
    price: float = None

    @validator('*')
    def check_null(cls, v,field):
        if v is None or v == "":
            raise HTTPException(status_code=404, detail=f"El campo '{field.name}' es obligatorio.")
        return v

class DiscUpdate(BaseModel):
    album: str = None
    artist: str = None
    genre: str = None
    year: int = None
    price: float = None

    @validator('*')
    def check_null(cls, v,field):
        if v is None or v == "":
            raise HTTPException(status_code=404, detail=f"El campo '{field.name}' es obligatorio.")
        return v

class SpotifyDisc(BaseModel):
    id:  str = None
    album: str = None
    artist: str = None
    year: int = None
    cover_picture: str = None

