# app/services/oneroster_data_service.py
from typing import List, Optional, Dict, Any
from app.connectors.oneroster_processor import get_processed_oneroster_data
from app.models.oneroster_models import (
    ProcessedOneRosterData, Org, User, Course, Class, Enrollment, AcademicSession
)  # Import your Pydantic models

# --- Simple In-Memory Cache (for PoC purposes) ---
# In a real app, use Redis, Memcached, or a proper database.
_cached_data: Optional[ProcessedOneRosterData] = None
_CACHE_TTL_SECONDS = 60  # Cache data for 60 seconds for this PoC
import time

_last_cache_time: float = 0.0


# --- End Cache ---

async def get_all_data() -> ProcessedOneRosterData:
    """
    Retrieves all processed OneRoster data, using a simple cache.
    """
    global _cached_data, _last_cache_time
    current_time = time.time()

    if _cached_data and (current_time - _last_cache_time < _CACHE_TTL_SECONDS):
        print("Returning cached OneRoster data.")
        return _cached_data

    print("Cache expired or empty. Reprocessing OneRoster data.")
    _cached_data = await get_processed_oneroster_data()  # This calls your existing processor
    _last_cache_time = current_time
    return _cached_data


# --- Service functions for specific OneRoster entities ---

async def get_orgs(limit: int = 100, offset: int = 0, filter_str: Optional[str] = None) -> List[Org]:
    data = await get_all_data()
    orgs = data.orgs
    # Basic filtering example (can be expanded significantly)
    if filter_str:
        # Example: ?filter=type='school'
        try:
            key, value_with_quotes = filter_str.split("=")
            value = value_with_quotes.strip("'\"")  # Remove quotes
            if hasattr(Org, key):  # Check if the key is a valid attribute of Org
                orgs = [org for org in orgs if getattr(org, key, None) == value]
        except ValueError:
            print(f"Warning: Could not parse filter: {filter_str}")
            # Potentially raise an error or return empty list based on spec
    return orgs[offset: offset + limit]


async def get_org_by_id(sourced_id: str) -> Optional[Org]:
    data = await get_all_data()
    return next((org for org in data.orgs if org.sourcedId == sourced_id), None)


async def get_users(limit: int = 100, offset: int = 0, filter_str: Optional[str] = None) -> List[User]:
    data = await get_all_data()
    users = data.users
    if filter_str:
        # Example: ?filter=role='student'
        try:
            key, value_with_quotes = filter_str.split("=")
            value = value_with_quotes.strip("'\"")
            if hasattr(User, key):
                users = [user for user in users if getattr(user, key, None) == value]
            elif key == "role":  # Specific handling for common filters
                users = [user for user in users if user.role.value == value]  # Role is an Enum
        except Exception as e:  # More general catch for complex filters
            print(f"Warning: Could not parse filter for users: {filter_str} - {e}")
    return users[offset: offset + limit]


async def get_user_by_id(sourced_id: str) -> Optional[User]:
    data = await get_all_data()
    return next((user for user in data.users if user.sourcedId == sourced_id), None)


async def get_classes(limit: int = 100, offset: int = 0, filter_str: Optional[str] = None) -> List[Class]:
    data = await get_all_data()
    classes = data.classes
    # Add filtering logic similar to get_orgs or get_users if needed
    if filter_str:
        try:
            key, value_with_quotes = filter_str.split("=")
            value = value_with_quotes.strip("'\"")
            if hasattr(Class, key):
                classes = [cls for cls in classes if str(getattr(cls, key, None)) == value]
            elif key == "schoolSourcedId":  # common filter
                classes = [cls for cls in classes if cls.schoolSourcedId == value]

        except Exception as e:
            print(f"Warning: Could not parse filter for classes: {filter_str} - {e}")
    return classes[offset: offset + limit]


async def get_class_by_id(sourced_id: str) -> Optional[Class]:
    data = await get_all_data()
    return next((cls for cls in data.classes if cls.sourcedId == sourced_id), None)


async def get_students_for_class(class_sourced_id: str, limit: int = 100, offset: int = 0) -> List[User]:
    data = await get_all_data()
    student_ids_in_class = {
        enr.userSourcedId
        for enr in data.enrollments
        if enr.classSourcedId == class_sourced_id and enr.role == "student"  # RoleType.STUDENT.value
    }
    students = [user for user in data.users if user.sourcedId in student_ids_in_class]
    return students[offset: offset + limit]


async def get_teachers_for_class(class_sourced_id: str, limit: int = 100, offset: int = 0) -> List[User]:
    data = await get_all_data()
    teacher_ids_in_class = {
        enr.userSourcedId
        for enr in data.enrollments
        if enr.classSourcedId == class_sourced_id and enr.role == "teacher"  # RoleType.TEACHER.value
    }
    teachers = [user for user in data.users if user.sourcedId in teacher_ids_in_class]
    return teachers[offset: offset + limit]

# Add more functions for courses, enrollments, academicSessions as needed
# e.g., get_courses, get_enrollments_for_user, etc.

# --- NEW Service functions ---
async def get_courses(limit: int = 100, offset: int = 0, filter_str: Optional[str] = None) -> List[Course]:
    data = await get_all_data()
    courses = data.courses
    if filter_str:
        try:
            key, value_with_quotes = filter_str.split("=")
            value = value_with_quotes.strip("'\"").lower()
            if hasattr(Course, key):
                courses = [c for c in courses if str(getattr(c, key, None)).lower() == value]
            elif key == "orgSourcedId":  # Common filter
                courses = [c for c in courses if c.orgSourcedId and c.orgSourcedId.lower() == value]

        except Exception as e:
            print(f"Warning: Could not parse filter for courses: {filter_str} - {e}")
    return courses[offset: offset + limit]


async def get_course_by_id(sourced_id: str) -> Optional[Course]:
    data = await get_all_data()
    return next((c for c in data.courses if c.sourcedId == sourced_id), None)


async def get_enrollments(limit: int = 100, offset: int = 0, filter_str: Optional[str] = None) -> List[Enrollment]:
    data = await get_all_data()
    enrollments = data.enrollments
    if filter_str:
        try:
            key, value_with_quotes = filter_str.split("=")
            value = value_with_quotes.strip("'\"").lower()
            if hasattr(Enrollment, key):
                enrollments = [e for e in enrollments if str(getattr(e, key, None)).lower() == value]
            elif key == "classSourcedId":
                enrollments = [e for e in enrollments if e.classSourcedId.lower() == value]
            elif key == "userSourcedId":
                enrollments = [e for e in enrollments if e.userSourcedId.lower() == value]
            elif key == "schoolSourcedId":
                enrollments = [e for e in enrollments if e.schoolSourcedId.lower() == value]
            elif key == "role":
                enrollments = [e for e in enrollments if e.role.value.lower() == value]
        except Exception as e:
            print(f"Warning: Could not parse filter for enrollments: {filter_str} - {e}")
    return enrollments[offset: offset + limit]


async def get_enrollment_by_id(sourced_id: str) -> Optional[Enrollment]:
    data = await get_all_data()
    return next((e for e in data.enrollments if e.sourcedId == sourced_id), None)


async def get_academic_sessions(limit: int = 100, offset: int = 0, filter_str: Optional[str] = None) -> List[
    AcademicSession]:
    data = await get_all_data()
    sessions = data.academicSessions
    if filter_str:
        try:
            key, value_with_quotes = filter_str.split("=")
            value = value_with_quotes.strip("'\"").lower()
            if hasattr(AcademicSession, key):
                sessions = [s for s in sessions if str(getattr(s, key, None)).lower() == value]
            elif key == "type":  # Common filter
                sessions = [s for s in sessions if s.type.lower() == value]
            elif key == "parentSourcedId":
                sessions = [s for s in sessions if s.parentSourcedId and s.parentSourcedId.lower() == value]
        except Exception as e:
            print(f"Warning: Could not parse filter for academic sessions: {filter_str} - {e}")
    return sessions[offset: offset + limit]


async def get_academic_session_by_id(sourced_id: str) -> Optional[AcademicSession]:
    data = await get_all_data()
    return next((s for s in data.academicSessions if s.sourcedId == sourced_id), None)


# Example: Get classes for a specific course
async def get_classes_for_course(course_sourced_id: str, limit: int = 100, offset: int = 0) -> List[Class]:
    data = await get_all_data()
    # First, check if course exists (optional, but good practice)
    course = await get_course_by_id(course_sourced_id)
    if not course:
        return []  # Or raise HTTPException(404) from router

    classes = [cls for cls in data.classes if cls.courseSourcedId == course_sourced_id]
    return classes[offset: offset + limit]