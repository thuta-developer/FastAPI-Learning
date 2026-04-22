from pydantic import BaseModel, EmailStr,ConfigDict
from typing import Optional, List
from uuid import UUID

# --- User Base (ဘုံတူညီတဲ့ field များ) ---
class UserBase(BaseModel):
    username: str
    email: EmailStr

# --- Request Schemas (Input) ---
class UserRegister(UserBase):
    password: str
    confirm_password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(UserBase): # Admin ကနေ staff အသစ်တွေ create လုပ်ဖို့
    password: str
    is_staff: Optional[bool] = False

# --- Response Schemas (Output) ---
class UserResponse(UserBase):
    id: UUID
    is_staff: bool

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    is_staff: bool

class TokenData(BaseModel):
    username: Optional[str] = None
    is_staff: bool = False



class ItemCreate(BaseModel):
    title: str
    description: str




class ItemUpdate(BaseModel):
    title : Optional[str] = None
    description : Optional[str] = None