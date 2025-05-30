# app/routers/oneroster_router.py
from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional
from app.services import oneroster_data_service as service # Import the new service
from app.models.oneroster_models import ( # Import Pydantic models for response_model
    Org, User, Class, Course, AcademicSession, Enrollment # Add others as you implement endpoints
)

# This router can be for your custom combined endpoint
custom_router = APIRouter(
    prefix="/api/v1/oneroster",
    tags=["Custom Processed OneRoster Data"],
)

@custom_router.get("/all", response_model=service.ProcessedOneRosterData) # Use the ProcessedOneRosterData model
async def read_all_processed_oneroster_data():
    """
    Retrieves all processed and transformed data in OneRoster v1.1 format
    from the connected source systems. (Custom endpoint)
    """
    data = await service.get_all_data() # Use the service
    return data


# New Router for standard OneRoster v1.1 endpoints
oneroster_v1p1_router = APIRouter(
    prefix="/ims/oneroster/v1p1", # Standard OneRoster base path
    tags=["OneRoster v1.1 API"],
    # TODO: Add dependencies for OAuth2 security here later
)

# --- Orgs Endpoints ---
@oneroster_v1p1_router.get("/orgs", response_model=List[Org])
async def get_all_orgs(
    limit: int = Query(100, ge=1, le=10000, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    filter: Optional[str] = Query(None, alias="filter", description="FIQL filter expression (basic support)")
):
    orgs = await service.get_orgs(limit=limit, offset=offset, filter_str=filter)
    # TODO: Set X-Total-Count header in the actual response for pagination
    return orgs

@oneroster_v1p1_router.get("/orgs/{sourcedId}", response_model=Org)
async def get_org(sourcedId: str = Path(..., description="The sourcedId of the organization")):
    org = await service.get_org_by_id(sourcedId)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

# --- Users Endpoints ---
@oneroster_v1p1_router.get("/users", response_model=List[User])
async def get_all_users(
    limit: int = Query(100, ge=1, le=10000),
    offset: int = Query(0, ge=0),
    filter: Optional[str] = Query(None, alias="filter") # Basic filter support
):
    users = await service.get_users(limit=limit, offset=offset, filter_str=filter)
    return users

@oneroster_v1p1_router.get("/users/{sourcedId}", response_model=User)
async def get_user(sourcedId: str = Path(..., description="The sourcedId of the user")):
    user = await service.get_user_by_id(sourcedId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# --- Classes Endpoints ---
@oneroster_v1p1_router.get("/classes", response_model=List[Class])
async def get_all_classes(
    limit: int = Query(100, ge=1, le=10000),
    offset: int = Query(0, ge=0),
    filter: Optional[str] = Query(None, alias="filter")
):
    classes = await service.get_classes(limit=limit, offset=offset, filter_str=filter)
    return classes

@oneroster_v1p1_router.get("/classes/{sourcedId}", response_model=Class)
async def get_class(sourcedId: str = Path(..., description="The sourcedId of the class")):
    cls = await service.get_class_by_id(sourcedId)
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    return cls

# --- Nested Resources (Examples) ---
@oneroster_v1p1_router.get("/classes/{sourcedId}/students", response_model=List[User])
async def get_students_in_class(
    sourcedId: str = Path(..., description="The sourcedId of the class"),
    limit: int = Query(100, ge=1, le=10000),
    offset: int = Query(0, ge=0)
):
    # First, check if class exists
    cls = await service.get_class_by_id(sourcedId)
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    students = await service.get_students_for_class(class_sourced_id=sourcedId, limit=limit, offset=offset)
    return students

@oneroster_v1p1_router.get("/classes/{sourcedId}/teachers", response_model=List[User])
async def get_teachers_in_class(
    sourcedId: str = Path(..., description="The sourcedId of the class"),
    limit: int = Query(100, ge=1, le=10000),
    offset: int = Query(0, ge=0)
):
    cls = await service.get_class_by_id(sourcedId)
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    teachers = await service.get_teachers_for_class(class_sourced_id=sourcedId, limit=limit, offset=offset)
    return teachers


# --- Courses Endpoints --- (NEW)
@oneroster_v1p1_router.get("/courses", response_model=List[Course])
async def get_all_courses(limit: int = Query(100, ge=1, le=10000), offset: int = Query(0, ge=0),
                          filter: Optional[str] = Query(None, alias="filter")):
    return await service.get_courses(limit=limit, offset=offset, filter_str=filter)


@oneroster_v1p1_router.get("/courses/{sourcedId}", response_model=Course)
async def get_course(sourcedId: str = Path(..., description="The sourcedId of the course")):
    course = await service.get_course_by_id(sourcedId)
    if not course: raise HTTPException(status_code=404, detail="Course not found")
    return course


@oneroster_v1p1_router.get("/courses/{sourcedId}/classes", response_model=List[Class])
async def get_classes_for_a_course(
        sourcedId: str = Path(..., description="The sourcedId of the course"),
        limit: int = Query(100, ge=1, le=10000),
        offset: int = Query(0, ge=0)
):
    # Service function get_classes_for_course already checks if course exists
    classes = await service.get_classes_for_course(course_sourced_id=sourcedId, limit=limit, offset=offset)
    if not classes and not await service.get_course_by_id(
            sourcedId):  # double check if course itself was not found vs no classes
        raise HTTPException(status_code=404, detail=f"Course with sourcedId '{sourcedId}' not found.")
    return classes


# --- Enrollments Endpoints --- (NEW)
@oneroster_v1p1_router.get("/enrollments", response_model=List[Enrollment])
async def get_all_enrollments(limit: int = Query(100, ge=1, le=10000), offset: int = Query(0, ge=0),
                              filter: Optional[str] = Query(None, alias="filter")):
    return await service.get_enrollments(limit=limit, offset=offset, filter_str=filter)


@oneroster_v1p1_router.get("/enrollments/{sourcedId}", response_model=Enrollment)
async def get_enrollment(sourcedId: str = Path(..., description="The sourcedId of the enrollment")):
    enrollment = await service.get_enrollment_by_id(sourcedId)
    if not enrollment: raise HTTPException(status_code=404, detail="Enrollment not found")
    return enrollment


# --- Academic Sessions Endpoints --- (NEW)
@oneroster_v1p1_router.get("/academicSessions", response_model=List[AcademicSession])
async def get_all_academic_sessions(limit: int = Query(100, ge=1, le=10000), offset: int = Query(0, ge=0),
                                    filter: Optional[str] = Query(None, alias="filter")):
    return await service.get_academic_sessions(limit=limit, offset=offset, filter_str=filter)


@oneroster_v1p1_router.get("/academicSessions/{sourcedId}", response_model=AcademicSession)
async def get_academic_session(sourcedId: str = Path(..., description="The sourcedId of the academic session")):
    session = await service.get_academic_session_by_id(sourcedId)
    if not session: raise HTTPException(status_code=404, detail="Academic Session not found")
    return session


# --- Other common nested resources (Examples) ---
@oneroster_v1p1_router.get("/users/{sourcedId}/classes", response_model=List[Class])
async def get_classes_for_user(
        sourcedId: str = Path(..., description="The sourcedId of the user"),
        limit: int = Query(100), offset: int = Query(0),
        role: Optional[str] = Query(None, description="Filter by role in the class (student, teacher)")
):
    user = await service.get_user_by_id(sourcedId)
    if not user: raise HTTPException(status_code=404, detail="User not found")

    all_data = await service.get_all_data()
    class_ids = set()
    for enr in all_data.enrollments:
        if enr.userSourcedId == sourcedId:
            if role and enr.role.value != role:  # RoleType enum
                continue
            class_ids.add(enr.classSourcedId)

    classes = [cls for cls in all_data.classes if cls.sourcedId in class_ids]
    return classes[offset: offset + limit]


# TODO: Implement more robust filtering, field selection, sorting as per OneRoster spec
# TODO: Add response headers like X-Total-Count for pagination