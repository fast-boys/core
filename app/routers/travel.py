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


@router.post("/create")
def create_trip(
    datas: str,
    internal_id: str = Depends(get_internal_id),
    db: Session = Depends(get_db),
):
    pass


@router.get("/plan/{plan_id}")
def get_plan_detail(
    plan_id: int,
    internal_id: str = Depends(get_internal_id),
    db: Session = Depends(get_db),
):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()

    place = IPlace(
        id=1,
        name="312",
        category=["312"],
        lat="312",
        long="312",
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
            # "travelTags": plan.tags,
            # "cities": plan.cities,
        }
    }
