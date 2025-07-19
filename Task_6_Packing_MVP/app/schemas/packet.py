from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import re

class SUserGetPack(BaseModel):
    user_id: int = Field(..., description="Идентификатор пользователя")

class SPacketName(BaseModel):
    aname: str = Field(default="")

class SPacketID(BaseModel):
    packet_id: int = Field(..., description="Идентификатор пакета")

class SPacketAdd(BaseModel):
    user_id: int = Field(..., description="Идентификатор пользователя")
    aname: str = Field(default="")

class SPacketComplete(BaseModel):
    task_id: str  # или int, если ID числовой
    status: str  # например, "success" или "failed"
    result: Optional[str] = None  # результат в base64 или другом формате