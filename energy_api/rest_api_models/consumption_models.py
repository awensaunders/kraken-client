from pydantic import BaseModel
from datetime import datetime

class ConsumptionEntry(BaseModel):
    interval_start: datetime
    interval_end: datetime
    consumption: float

class PaginatedConsumption(BaseModel):
    count: int
    next: str | None
    previous: str | None
    results: list[ConsumptionEntry]
