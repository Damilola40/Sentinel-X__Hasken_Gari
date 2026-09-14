from pydantic import BaseModel, EmailStr #, ConfigDict
from typing import Literal, Optional
#from pydantic.alias_generators import to_camel
from uuid import UUID
from datetime import datetime

class AppUserIn(BaseModel):
    full_name: str
    phone_number:str
    email: EmailStr
    password: str

    class Config:
            from_attributes = True

class SmsUserIn(BaseModel):
    full_name: Optional[str] = None
    phone_number:str
    email: Optional[EmailStr] = None

    class Config:
            from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
            from_attributes = True

class Token(BaseModel):
      access_token: str
      token_type: str

class TokenData(BaseModel):
      id: Optional[str] = None

class UserPatch(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None

    class Config:
            from_attributes = True

class UserData(BaseModel):
    id: UUID
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: str
    role: Literal["admin", "responder", "citizen"]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
                from_attributes = True
    