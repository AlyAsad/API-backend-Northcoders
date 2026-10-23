from pydantic import BaseModel
from datetime import datetime


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class _RegisterResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime


class RegisterResponse(BaseModel):
    user: _RegisterResponse