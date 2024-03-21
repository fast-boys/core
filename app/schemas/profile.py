from typing import List, Dict, Optional
from pydantic import BaseModel


class Place(BaseModel):
    id: str
    name: str
    category: List[str]


class DayPlan(BaseModel):
    id: str
    day: str
    placeIds: List[str]


class Info(BaseModel):
    name: str
    profileImage: str
    startDate: str
    endDate: str
    travelTags: List[str]
    cities: List[str]


class Plan(BaseModel):
    places: Dict[str, Place]
    days: Dict[str, DayPlan]
    dayOrder: List[str]


class ITravelDetail(BaseModel):
    id: str
    info: Info
    plan: Plan


class TravelDetailResponse(BaseModel):
    data: ITravelDetail
