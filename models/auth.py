from pydantic import BaseModel


class LoginRequest(BaseModel):
    id: int
    title: str
    starts_at: datetime
    ends_at: datetime
    location: str