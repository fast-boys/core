import datetime
from typing import Optional
from pydantic import BaseModel


class TravelResponse(BaseModel):
    travelId: int
    travelImage: Optional[str] = None
    travelName: str
    startDate: datetime.date
    endDate: datetime.date
    numOfCity: int
