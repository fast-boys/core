import os
from fastapi import APIRouter, Depends, Path, Request, Response
from fastapi.security import HTTPBearer

from database import get_db, get_m_db
from sqlalchemy.orm import Session

router = APIRouter(tags=["place"], prefix="/place")


@router.get("/{id}")
def get_place_info(
    m_db: Session = Depends(get_m_db),
    id: str = Path(...),
):
    place_info = m_db.find_one({"spot_id": {"$eq": id}})
    return place_info
