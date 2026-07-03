
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico del usuario y que sea valido")
    full_name: Optional[str] = Field(None, max_length=100, description="Nombre completo del usuario")

class UserCreate(UserBase):
        password: str = Field(..., min_length=8, max_length=64, description="Contraseña del usuario")


class UserResponse(UserBase):
        id: uuid.UUID
        is_admin: bool
        is_active: bool
        created_at: datetime

        
        model_config = {
            "from_attributes": True,
        }



class UserLogin(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

