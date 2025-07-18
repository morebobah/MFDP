from pydantic import BaseModel, EmailStr, Field
import re

class SAdminID(BaseModel):
    id: int = Field(..., gt=0)

class SAdminEmail(BaseModel):
    email: EmailStr
    