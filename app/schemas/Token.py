from typing import List, Union, Optional
from fastapi import HTTPException
from pydantic import BaseModel, Field, Required, validator
from datetime import datetime

'''

    Token

'''
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Union[str, None] = None
    scopes: List[str] = []

