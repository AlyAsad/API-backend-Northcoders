from pydantic import BaseModel


class _GetOrganiserStats(BaseModel):
    organiser_id: int
    name: str
    total_events: int
    avg_attendance: float
    best_attended_count: int
    organiser_rank: int


class GetOrganiserStats(BaseModel):
    stats: _GetOrganiserStats
