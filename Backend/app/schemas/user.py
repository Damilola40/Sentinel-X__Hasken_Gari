from pydantic import BaseModel, EmailStr
from typing import Literal, Optional

class AppUserIn(BaseModel):
    username: str
    phone_number:str
    email: EmailStr
    password: str
    role: Literal["admin", "responder", "citizen"]

class SmsUserIn(BaseModel):
    username: Optional[str] = None
    phone_number:str
    email: Optional[EmailStr] = None

class UserOut(BaseModel):
    user_id: str
    username: Optional[str] = None
    phone_number: str
    email: Optional[EmailStr] = None
    role: Literal["admin", "responder", "citizen"]