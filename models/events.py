from pydantic import BaseModel
from datetime import datetime


class Event(BaseModel):
    id: int
    title: str
    starts_at: datetime
    ends_at: datetime
    location: str | None



class EventResponse(BaseModel):
    events: list[Event]