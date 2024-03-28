import json
import os
from typing import List
from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
    Response,
    UploadFile,
)

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from routers.place import get_details
from models.plan import Plan
from schemas.travel import (
    IPlace,
    IPlan,
    MySpotRequest,
    MySpotResponse,
    PlanDetailResponse,
    TravelResponse,
    TripCreateForm,
)
from models.user import User
from database import get_db, get_m_db
from sqlalchemy.orm import Session

from services.profile import get_internal_id

router = APIRouter(tags=["trip"], prefix="/travel")


@router.get("/list")
async def get_trip_list(
    request: Request,
    response: Response,
    internal_id: str = Depends(get_internal_id),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.internal_id == internal_id).first()
    response = []
    if user:
        # User에 연결된 Plan 목록에 접근합니다.
        plans = user.plans
        # plans는 Plan 인스턴스의 리스트입니다. 필요에 따라 이를 처리할 수 있습니다.
        for plan in plans:
            res = TravelResponse(
                travelId=plan.id,
                travelImage=plan.title_image_url,
                travelName=plan.name,
                startDate=plan.start_date,
                endDate=plan.end_date,
                numOfCity=len(plan.plan_citys),
            )
            response.append(res)
        return response

    raise HTTPException(status_code=401, detail="Unauthorized user")


@router.get("/like/list")
async def get_like_trip_list(
    request: Request,
    response: Response,
    internal_id: str = Depends(get_internal_id),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.internal_id == internal_id).first()
    response = []
    if user:
        # User에 연결된 UserPlan 목록에 접근합니다.
        my_spots = user.my_spots
        # user_plans는 UserPlan 인스턴스의 리스트입니다. 필요에 따라 이를 처리할 수 있습니다.
        for my_spot in my_spots:
            res = MySpotResponse(
                locationId=1,
                locationImage="/src/assets/svgs/travelImage.svg",
                locationName="홉히",
                locationAddress="제주 시내(제주)",
                locationMemo="크림 쏟아버렸던 그 곳.. 찐맛이었다. 또 가고 싶다.",
            )
            response.append(res)
        return response

    raise HTTPException(status_code=401, detail="Unauthorized user")


@router.put("/create")
def create_trip(
    profileName: str = Form(...),
    profileImage: UploadFile = Form(...),
    startDate: str = Form(...),
    endDate: str = Form(...),
    cities: str = Form(...),
    internal_id: str = Depends(get_internal_id),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.internal_id == internal_id).first()

    trip_data = TripCreateForm(
        profileName=profileName,
        startDate=startDate.split("T")[0],  # Pydantic이 자동으로 date 객체로 변환
        endDate=endDate.split("T")[0],  # Pydantic이 자동으로 date 객체로 변환
        cities=json.loads(cities),
    )
    plan = Plan(
        creator_id=user.id,
        name=trip_data.profileName,
        start_date=trip_data.startDate,
        end_date=trip_data.endDate,
        cities=trip_data.cities,
    )
    db.add(plan)
    db.commit()
    print(trip_data)
    # print(profileName, startDate, endDate, cities)
    # print(profileImage.filename)
    # print(internal_id)


@router.get("/plan/{plan_id}")
async def get_plan_detail(
    plan_id: int,
    internal_id: str = Depends(get_internal_id),
    db: Session = Depends(get_db),
    collection: Session = Depends(get_m_db),
):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    places = []
    dayorder = set()
    days = dict()
    for place in plan.visit_places:
        spot_id = place.spot_id
        date = place.date
        # 지역 정보 탐색
        tour_spot = await get_details(spot_id, collection)
        place = IPlace(
            id=tour_spot.id,
            name=tour_spot.name,
            category=tour_spot.category,
            lat=tour_spot.lat,
            long=tour_spot.long,
        )
        places.append(place)
        # 날짜별 정보
        dayorder.add(date)

    plan = IPlan(
        places=places,
        start_date=plan.start_date,
        end_date=plan.end_date,
        spot=place,
    )
    plan_detail_response = PlanDetailResponse(
        id=plan_id,
        info={},
        plan={},
    )
    plan_detail_response.info = {
        "info": {
            "name": plan.name,
            "profileImage": plan.title_image_url,
            "startDate": plan.start_date,
            "endDate": plan.end_date,
            # "cities": plan.cities,
        }
    }
