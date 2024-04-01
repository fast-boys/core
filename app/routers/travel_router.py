from io import BytesIO
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

from services.gcs import (
    create_plan_secure_path,
    create_secure_path,
    process_profile_image,
    upload_to_open_gcs,
)
from routers.spot_router import get_details
from models.plan import Plan
from schemas.travel_dto import (
    IEditDetailPlanRequest,
    IPlan,
    ISpot,
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
                planId=plan.id,
                planImage=plan.title_image_url,
                planName=plan.name,
                startDate=plan.start_date,
                endDate=plan.end_date,
                numOfCity=len(plan.cities),
            )
            response.append(res)
        return response

    raise HTTPException(status_code=401, detail="Unauthorized user")


@router.put("/create")
async def create_trip(
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
    db.refresh(plan)

    if profileImage and profileImage.filename:
        image_data = await profileImage.read()
        image_stream = BytesIO(image_data)
        # 이미지 처리
        processed_image = process_profile_image(image_stream)
        destination_blob_name = create_plan_secure_path(plan.id, "png")

        # 이미지를 GCP에 업로드하고 사인된 URL을 가져옴
        public_url = upload_to_open_gcs(processed_image, destination_blob_name)
        plan.title_image_url = public_url

    db.commit()
    db.refresh(plan)

    return {
        "planId": plan.id,
        "planImage": plan.title_image_url,
        "planName": plan.name,
        "startDate": plan.start_date,
        "endDate": plan.end_date,
        "numOfCity": len(plan.cities),
    }


@router.get("/plan/{plan_id}")
async def get_plan_detail(
    plan_id: int,
    internal_id: str = Depends(get_internal_id),
    db: Session = Depends(get_db),
    collection: Session = Depends(get_m_db),
):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    places = {}
    dayorder = set()
    days = {}

    for visited_spot in plan.visit_spots:
        spot_id = visited_spot.spot_id
        date = visited_spot.date
        # 지역 정보 탐색
        tour_spot = await get_details(spot_id, collection)
        spot = ISpot(
            id=tour_spot.id,
            name=tour_spot.name,
            category=tour_spot.category,
            lat=tour_spot.lat,
            long=tour_spot.long,
        )
        places.append({spot_id: spot})
        # 날짜별 정보
        dayorder.add(date)

        if visited_spot.date not in days:
            days[visited_spot.date] = []
        else:
            days[visited_spot.date].add("spot_id")
    print(list(dayorder))
    iplan = IPlan(
        places=places,
        days=days,
        dayOrder=list(dayorder),
    )

    plan_detail_response = PlanDetailResponse(
        id=plan_id,
        info={},
        plan=iplan,
    )
    plan_detail_response.info = {
        "info": {
            "name": plan.name,
            "profileImage": plan.title_image_url,
            "startDate": plan.start_date,
            "endDate": plan.end_date,
            "cities": plan.cities,
        }
    }
    return plan_detail_response


@router.put("/plan/{plan_id}")
async def get_plan_detail(
    edit_plan: IEditDetailPlanRequest,
    internal_id: str = Depends(get_internal_id),
    db: Session = Depends(get_db),
    collection: Session = Depends(get_m_db),
):
    plan = db.query(Plan).filter(Plan.id == edit_plan.planId).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    for detail_plan in edit_plan.plans:
        # plan.visit_spots를 초기화 후 다시 추가
        plan.visit_spots = []
        plan.visit_spots.append(
            {
                "spot_id": detail_plan.spotId,
                "date": detail_plan.date,
            }
        )
    db.commit()
    return JSONResponse(status_code=200, content={"message": "success"})
