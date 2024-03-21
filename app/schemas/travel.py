import datetime
from pydantic import BaseModel


class TravelResponse(BaseModel):
    travelId: str
    travelImage: str
    travelName: str
    startDate: datetime.datetime
    endDate: datetime.datetime
    numOfCity: int
