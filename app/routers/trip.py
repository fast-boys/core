import os
from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import HTTPBearer

from app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(tags=["trip"])
