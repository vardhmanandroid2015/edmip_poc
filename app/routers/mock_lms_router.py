# app/routers/mock_lms_router.py
from fastapi import APIRouter
from typing import List, Dict, Any
from app.mock_systems import lms # Import your mock LMS module

router = APIRouter(
    prefix="/mock/lms",
    tags=["Mock LMS System"],
)

@router.get("/courses", response_model=List[Dict[str, Any]])
async def read_lms_courses():
    return lms.get_lms_courses()

@router.get("/users", response_model=List[Dict[str, Any]])
async def read_lms_users():
    return lms.get_lms_users()