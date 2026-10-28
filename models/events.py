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


class _RSVPResponse(BaseModel):
    id: int
    attendee_id : int
    event_id : int
    created_at: datetime


class RSVPResponse(BaseModel):
    rsvp: _RSVPResponse


class EventPostRequest(BaseModel):
    title: str
    description: str
    starts_at: datetime
    ends_at: datetime
    venue_id: int

class _EventPostResponse(BaseModel):
    id: int
    title: str
    description: str
    starts_at: datetime
    ends_at: datetime
    venue_id: int
    organiser_id: int
    created_at: datetime
    
class EventPostResponse(BaseModel):
    event: _EventPostResponse