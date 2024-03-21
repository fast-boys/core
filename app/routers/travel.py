import os
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from schemas.travel import TravelResponse
from models.user import User
from database import get_db
from sqlalchemy.orm import Session

from services.utils import get_internal_id

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
