# app/connectors/lms_connector.py
import httpx
from typing import List, Dict, Any, Tuple
from app.models.oneroster_models import User, Course, RoleType, StatusType

# We might not create all OneRoster entities from LMS if SIS is primary.
# For example, LMS might just give us users and its own course view.

# Base URL for your FastAPI app (where mock services are running)
MOCK_API_BASE_URL = "http://127.0.0.1:8006"  # Or your actual port


async def fetch_lms_data() -> Tuple[List[Dict], List[Dict]]:
    """Fetches all necessary data from the mock LMS."""
    async with httpx.AsyncClient() as client:
        print(f"Fetching LMS users from: {MOCK_API_BASE_URL}/mock/lms/users")
        users_resp = await client.get(f"{MOCK_API_BASE_URL}/mock/lms/users")
        print(f"LMS Users response status: {users_resp.status_code}")
        print(f"LMS Users response content: {users_resp.text}")
        users_resp.raise_for_status()

        print(f"Fetching LMS courses from: {MOCK_API_BASE_URL}/mock/lms/courses")
        courses_resp = await client.get(f"{MOCK_API_BASE_URL}/mock/lms/courses")
        print(f"LMS Courses response status: {courses_resp.status_code}")
        print(f"LMS Courses response content: {courses_resp.text}")
        courses_resp.raise_for_status()

        try:
            lms_users = users_resp.json()
            lms_courses = courses_resp.json()
        except Exception as e:
            print(f"LMS JSON parsing error: {e}")
            raise

        return lms_users, lms_courses


def transform_lms_users(lms_users_data: List[Dict]) -> List[User]:
    oneroster_lms_users: List[User] = []
    for lms_user in lms_users_data:
        # Determine OneRoster role from LMS role
        role = RoleType.STUDENT  # Default
        if lms_user.get("role", "").lower() == "instructor":
            role = RoleType.TEACHER
        elif lms_user.get("role", "").lower() == "student":
            role = RoleType.STUDENT

        # Simple name parsing if full_name is provided
        given_name = lms_user.get("full_name", "").split(" ")[0] if lms_user.get("full_name") else "Unknown"
        family_name = " ".join(lms_user.get("full_name", "").split(" ")[1:]) if lms_user.get(
            "full_name") and " " in lms_user.get("full_name") else "User"

        user = User(
            sourcedId=f"lms_user_{lms_user['lms_username']}",  # Use LMS username for sourcedId prefix
            username=lms_user['lms_username'],
            givenName=given_name,
            familyName=family_name,
            email=lms_user.get('email'),
            role=role,
            identifier=lms_user['lms_username'],  # Could be different in a real scenario
            status=StatusType.ACTIVE,
            # agentSourcedIds and grades would typically come from SIS,
            # unless LMS is authoritative for some school/program.
            # For now, we leave them empty or default.
            agentSourcedIds=[],
        )
        oneroster_lms_users.append(user)
    return oneroster_lms_users


def transform_lms_courses(lms_courses_data: List[Dict]) -> List[Course]:
    """
    Transforms LMS courses into OneRoster Course format.
    Note: LMS courses might be more specific than SIS-defined courses.
    Reconciliation with SIS courses is a complex step not fully covered here.
    """
    oneroster_lms_courses: List[Course] = []
    current_school_year_sid = "default_ay_2023-2024"  # Placeholder, match SIS connector

    for lms_course in lms_courses_data:
        # We use LMS specific sourcedId. If external_sis_course_id exists,
        # it could be used for linking/merging with SIS courses in a more advanced scenario.
        course_sourced_id = f"lms_course_{lms_course['lms_course_id']}"

        # Attempt to get a general course code if an external SIS ID is provided
        course_code = lms_course.get('external_sis_course_id', lms_course['lms_course_id'])

        course = Course(
            sourcedId=course_sourced_id,
            title=lms_course['course_name'],
            courseCode=course_code,  # Could be the LMS ID or a mapped SIS code
            schoolYearSourcedId=current_school_year_sid,
            # orgSourcedId (school) for LMS courses might be tricky if LMS is district-wide
            # and not school-specific. For now, we'll omit or use a default if known.
            # orgSourcedId="sis_org_SCH001", # Example: if all LMS courses are for this school
            status=StatusType.ACTIVE,
            metadata={"lms_specific_id": lms_course['lms_course_id']}  # Store original LMS ID
        )
        oneroster_lms_courses.append(course)
    return oneroster_lms_courses


async def process_lms_to_oneroster_like_data() -> Dict[str, List[Any]]:
    """
    Main function for LMS connector: fetches and transforms LMS data
    into a structure resembling OneRoster entities.
    """
    lms_users_data, lms_courses_data = await fetch_lms_data()

    oneroster_like_lms_users = transform_lms_users(lms_users_data)
    oneroster_like_lms_courses = transform_lms_courses(lms_courses_data)

    # For this phase, we're not creating LMS-specific OneRoster enrollments or classes
    # as SIS is considered primary for those. This data is mostly for potential user/course matching.
    return {
        "users": [user.model_dump() for user in oneroster_like_lms_users],
        "courses": [course.model_dump() for course in oneroster_like_lms_courses],
    }