import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel
from datetime import date


class TripCreateForm(BaseModel):
    profileName: str
    startDate: date
    endDate: date
    cities: List[int]


class TravelResponse(BaseModel):
    planId: int
    planImage: Optional[str] = None
    planName: str
    startDate: datetime.date
    endDate: datetime.date
    numOfCity: int


class MySpotRequest(BaseModel):
    """
    사용자 좋아요 갱신 시 필요한 정보,
    """

    spot_id: str  # 관광지 고유 식별자
    is_like: bool


class MySpotResponse(BaseModel):
    locationId: int
    locationImage: Optional[str] = None
    locationName: str
    locationAddress: str
    locationMemo: Optional[str] = None


class IPlace(BaseModel):
    id: int
    name: str
    category: List[str]
    lat: str
    long: str


class IDay(BaseModel):
    id: int
    day: str
    placeIds: List[str]


class IPlan(BaseModel):
    places: Dict[str, IPlace]
    days: Dict[str, IDay]
    dayOrder: List[str]


class PlanDetailResponse(BaseModel):
    id: int
    info: dict
    plan: IPlan

    class Config:
        fields = {
            "info": {
                "name": Optional[str],
                "profileImage": Optional[str],
                "startDate": Optional[datetime.datetime],
                "endDate": Optional[datetime.datetime],
                "cities": Optional[List[str]],
            }
        }
