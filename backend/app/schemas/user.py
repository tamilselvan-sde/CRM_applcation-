from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str] = []


class RoleResponse(RoleBase):
    id: str = Field(alias="_id")

    class Config:
        populate_by_name = True


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(min_length=8)
    role: str = "viewer"


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: str = Field(alias="_id")
    role: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    permissions: List[str] = []
