from pydantic import BaseModel
from datetime import datetime


class _GetUserEvents(BaseModel):
    id: int
    title: str
    starts_at: datetime
    rsvp_date: datetime
    event_rank: int
    total_rsvps: int


class GetUserEvents(BaseModel):
    events: list[_GetUserEvents]
