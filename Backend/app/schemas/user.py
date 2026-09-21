from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Literal, Optional
from pydantic.alias_generators import to_camel
from uuid import UUID
from datetime import datetime

class AppUserIn(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    full_name: str
    phone_number:str
    email: EmailStr
    password: str


class SmsUserIn(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    full_name: Optional[str] = None
    phone_number:str
    email: Optional[EmailStr] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
      
    access_token: str
    token_type: str

class TokenData(BaseModel):
      id: Optional[str] = None

class UserPatch(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, 
                              from_attributes=True,
                              populate_by_name=True)

    full_name: Optional[str] = None
    phone_number: Optional[str] = None

class UserData(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: UUID
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: str
    role: Literal["admin", "responder", "citizen"]
    created_at: datetime
    updated_at: Optional[datetime] = None
    