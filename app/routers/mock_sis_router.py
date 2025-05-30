# app/routers/mock_sis_router.py
from fastapi import APIRouter
from typing import List, Dict, Any
from app.mock_systems import sis # Import your mock SIS module

router = APIRouter(
    prefix="/mock/sis",
    tags=["Mock SIS System"],
)

@router.get("/students", response_model=List[Dict[str, Any]])
async def read_sis_students():
    return sis.get_sis_students()

@router.get("/teachers", response_model=List[Dict[str, Any]])
async def read_sis_teachers():
    return sis.get_sis_teachers()

@router.get("/courses", response_model=List[Dict[str, Any]])
async def read_sis_courses():
    return sis.get_sis_courses()

@router.get("/orgs", response_model=List[Dict[str, Any]])
async def read_sis_orgs():
    return sis.get_sis_orgs()