from pydantic import BaseModel, EmailStr, Field
import re

class SUserAuth(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=3, max_length=50, description="Пароль, от 3 до 50 знаков")

class SUserRegister(BaseModel):
    first_name: str = Field(..., min_length=3, max_length=50, description="Имя, от 3 до 50 символов")
    last_name: str = Field(..., min_length=3, max_length=50, description="Фамилия, от 3 до 50 символов")
    email: EmailStr
    password: str = Field(..., min_length=3, max_length=150, description="Пароль, от 3 до 50 знаков")

class SUser(BaseModel):
    first_name: str = Field(..., min_length=3, max_length=50, description="Имя, от 3 до 50 символов")
    last_name: str = Field(..., min_length=3, max_length=50, description="Фамилия, от 3 до 50 символов")
    email: EmailStr
    password: str = Field(..., min_length=3, max_length=150, description="Пароль, от 3 до 150 знаков")
    is_admin: bool = Field(...)


class SUserInfo(BaseModel):
    id: int = Field(...)
    first_name: str = Field(..., min_length=3, max_length=50, description="Имя, от 3 до 50 символов")
    last_name: str = Field(..., min_length=3, max_length=50, description="Фамилия, от 3 до 50 символов")
    email: EmailStr
    is_admin: bool = Field(...)


class SUserID(BaseModel):
    id: int = Field(...)

class SUserEmail(BaseModel):
    email: EmailStr
