from typing import List, Union, Optional
from fastapi import HTTPException
from pydantic import BaseModel, Field, Required, validator
from datetime import datetime

'''

    AUTH

'''
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Union[str, None] = None
    scopes: List[str] = []


class Var(BaseModel):
    id: int
    name: Optional[str] = Field(nullable=True)
    value: Optional[str] = Field(nullable=True)
    description: Optional[str] = Field(nullable=True)
    service: Optional[int] = Field(nullable=True)
    status: Optional[float] = Field(nullable=True)

    class Config:
        orm_mode = True


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

'''
    FILE
'''
class File(BaseModel):
    id: int
    file_type: Optional[str] = Field(nullable=True)
    file_name: Optional[str] = Field(nullable=True)
    file_size: Optional[str] = Field(nullable=True)
    file_path: Optional[str] = Field(nullable=True)
    file_extension: Optional[str] = Field(nullable=True)

    class Config:
        orm_mode = True

class FileCreate(BaseModel):
    file_type: str = None
    file_name: str = None
    file_size: str = None
    file_path: str = None
    file_extension: str = None



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

class UserDisc(BaseModel):
    id: int
    album: Optional[str] = Field(nullable=True)
    artist: Optional[str] = Field(nullable=True)
    genre: Optional[str] = Field(nullable=True)
    year: Optional[int] = Field(nullable=True)
    price: Optional[float] = Field(nullable=True)
    cover_picture: Optional[str] = Field(nullable=True)
    purchase_date: datetime = None
