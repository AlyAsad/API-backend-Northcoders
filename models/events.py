from pydantic import BaseModel
from datetime import datetime


class EventForList(BaseModel):
    id: int
    title: str
    starts_at: datetime
    ends_at: datetime
    location: str



class AllEvents(BaseModel):
    events: list[EventForList]


class FullEvent(BaseModel):
    id: int
    title: str
    description: str
    starts_at: datetime
    ends_at: datetime
    location: str
    address: str | None
    capacity: int
    created_at: datetime

class EventResponse(BaseModel):
    event: FullEvent