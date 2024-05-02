from typing import List, Union, Optional
from fastapi import HTTPException
from pydantic import BaseModel, Field, Required, validator
from datetime import datetime

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


