import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel


class TravelResponse(BaseModel):
    travelId: int
    travelImage: Optional[str] = None
    travelName: str
    startDate: datetime.date
    endDate: datetime.date
    numOfCity: int


class MySpotResponse(BaseModel):
    locationId: int
    locationImage: Optional[str] = None
    locationName: str
    locationAddress: str
    locationMemo: Optional[str] = None


class IPlace(BaseModel):
    id: str
    name: str
    category: List[str]
    lat: str
    long: str


class IDay(BaseModel):
    id: str
    day: str
    placeIds: List[str]


class IPlan(BaseModel):
    places: Dict[str, IPlace]
    days: Dict[str, IDay]
    dayOrder: List[str]


class PlanDetailResponse(BaseModel):
    id: str
    info: dict
    plan: IPlan

    class Config:
        fields = {
            "info": {
                "name": "name",
                "profileImage": "profileImage",
                "startDate": "startDate",
                "endDate": "endDate",
                "travelTags": "travelTags",
                "cities": "cities",
            }
        }
