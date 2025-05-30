# app/connectors/sis_connector.py
import httpx
from typing import List, Dict, Any, Tuple
from app.models.oneroster_models import Org, User, Course, Class, Enrollment, AcademicSession, RoleType, OrgType, \
    ClassType, StatusType
import uuid
from datetime import datetime

# Base URL for your FastAPI app (where mock services are running)
# Ensure this matches the port you are running Uvicorn on for Phase 1
MOCK_API_BASE_URL = "http://127.0.0.1:8006"  # Or 8001, etc.


async def fetch_sis_data() -> Tuple[List[Dict], List[Dict], List[Dict], List[Dict]]:
    """Fetches all necessary data from the mock SIS."""
    async with httpx.AsyncClient() as client:
        orgs_resp = await client.get(f"{MOCK_API_BASE_URL}/mock/sis/orgs")
        students_resp = await client.get(f"{MOCK_API_BASE_URL}/mock/sis/students")
        teachers_resp = await client.get(f"{MOCK_API_BASE_URL}/mock/sis/teachers")
        courses_resp = await client.get(f"{MOCK_API_BASE_URL}/mock/sis/courses")  # SIS "course offerings"

        orgs_resp.raise_for_status()
        students_resp.raise_for_status()
        teachers_resp.raise_for_status()
        courses_resp.raise_for_status()

        return (
            orgs_resp.json(),
            students_resp.json(),
            teachers_resp.json(),
            courses_resp.json(),
        )


def transform_sis_orgs(sis_orgs_data: List[Dict]) -> List[Org]:
    oneroster_orgs: List[Org] = []
    for sis_org in sis_orgs_data:
        org_type_map = {"district": OrgType.DISTRICT, "school": OrgType.SCHOOL}
        org = Org(
            sourcedId=f"sis_org_{sis_org['org_id']}",
            name=sis_org['org_name'],
            type=org_type_map.get(sis_org['org_type'], OrgType.SCHOOL),  # Default if type unknown
            identifier=sis_org['org_id'],
            parentSourcedId=f"sis_org_{sis_org['parent_org_id']}" if sis_org.get('parent_org_id') else None,
            status=StatusType.ACTIVE  # Assuming all are active for simplicity
        )
        oneroster_orgs.append(org)
    return oneroster_orgs


def transform_sis_users_and_enrollments(
        sis_students_data: List[Dict],
        sis_teachers_data: List[Dict],
        sis_courses_data: List[Dict]  # Used to find school for enrollments and class schoolSourcedId
) -> Tuple[List[User], List[Enrollment]]:
    oneroster_users: List[User] = []
    oneroster_enrollments: List[Enrollment] = []

    # Process students
    for sis_student in sis_students_data:
        # Find the school the student is primarily associated with (e.g., via a course enrollment)
        # This is a simplification; a real SIS might have direct school association.
        student_school_id = None
        if sis_student.get("enrollments"):
            first_class_id = sis_student["enrollments"][0]["class_id"]
            for sis_course in sis_courses_data:
                if sis_course["course_code"] == first_class_id:
                    student_school_id = f"sis_org_{sis_course['school_id']}"
                    break

        user = User(
            sourcedId=f"sis_user_student_{sis_student['sis_student_id']}",
            username=f"{sis_student['first_name'][0].lower()}{sis_student['last_name'].lower()}",
            # Simple username generation
            givenName=sis_student['first_name'],
            familyName=sis_student['last_name'],
            email=sis_student.get('email_address'),
            role=RoleType.STUDENT,
            identifier=sis_student['sis_student_id'],
            agentSourcedIds=[student_school_id] if student_school_id else [],
            grades=[sis_student['grade_level']] if sis_student.get('grade_level') else None,
            status=StatusType.ACTIVE
        )
        oneroster_users.append(user)

        for enrollment in sis_student.get("enrollments", []):
            class_sourced_id = f"sis_class_{enrollment['class_id']}_{enrollment['section']}"  # Create a unique class sourcedId
            school_sourced_id_for_enrollment = student_school_id  # Assume enrollment school is student's school

            if school_sourced_id_for_enrollment:  # Only create enrollment if school is known
                enr = Enrollment(
                    sourcedId=f"sis_enr_stu_{sis_student['sis_student_id']}_{enrollment['class_id']}_{enrollment['section']}",
                    userSourcedId=user.sourcedId,
                    classSourcedId=class_sourced_id,
                    schoolSourcedId=school_sourced_id_for_enrollment,
                    role=RoleType.STUDENT,
                    primary=True,  # Assuming primary for simplicity
                    status=StatusType.ACTIVE
                )
                oneroster_enrollments.append(enr)

    # Process teachers
    for sis_teacher in sis_teachers_data:
        teacher_school_id = None  # Simplification: Assume teacher might teach at multiple schools
        # Or derive from their first assigned class.
        if sis_teacher.get("assigned_classes"):
            first_class_id = sis_teacher["assigned_classes"][0]["class_id"]
            for sis_course in sis_courses_data:
                if sis_course["course_code"] == first_class_id:
                    teacher_school_id = f"sis_org_{sis_course['school_id']}"
                    break

        user = User(
            sourcedId=f"sis_user_teacher_{sis_teacher['sis_teacher_id']}",
            username=f"{sis_teacher['staff_first_name'][0].lower()}{sis_teacher['staff_last_name'].lower()}",
            givenName=sis_teacher['staff_first_name'],
            familyName=sis_teacher['staff_last_name'],
            email=sis_teacher.get('primary_email'),
            role=RoleType.TEACHER,
            identifier=sis_teacher['sis_teacher_id'],
            agentSourcedIds=[teacher_school_id] if teacher_school_id else [],
            status=StatusType.ACTIVE
        )
        oneroster_users.append(user)

        for assignment in sis_teacher.get("assigned_classes", []):
            class_sourced_id = f"sis_class_{assignment['class_id']}_{assignment['section']}"
            school_sourced_id_for_enrollment = teacher_school_id

            if school_sourced_id_for_enrollment:
                enr = Enrollment(
                    sourcedId=f"sis_enr_tea_{sis_teacher['sis_teacher_id']}_{assignment['class_id']}_{assignment['section']}",
                    userSourcedId=user.sourcedId,
                    classSourcedId=class_sourced_id,
                    schoolSourcedId=school_sourced_id_for_enrollment,  # School where the class is taught
                    role=RoleType.TEACHER,
                    primary=(assignment.get("role", "").lower() == "primary"),
                    status=StatusType.ACTIVE
                )
                oneroster_enrollments.append(enr)

    return oneroster_users, oneroster_enrollments


def transform_sis_courses_and_classes(sis_courses_data: List[Dict]) -> Tuple[List[Course], List[Class]]:
    """
    SIS "courses" data often represents specific sections or offerings.
    We'll create OneRoster Courses (more general) and OneRoster Classes (specific instances).
    This is a common transformation pattern.
    """
    oneroster_courses: List[Course] = []
    oneroster_classes: List[Class] = []

    # For simplicity, assume academic session is known (e.g., current year)
    # In a real system, this would come from SIS or be configured.
    current_school_year_sid = "default_ay_2023-2024"  # Placeholder
    current_term_sid = "default_term_fall2023"  # Placeholder

    # Create unique OneRoster Courses from SIS course_codes
    # (e.g., MATH5A might be taught in multiple sections, but it's one OneRoster Course)
    unique_course_codes = {c['course_code']: c for c in sis_courses_data}

    for code, sis_course_offering_example in unique_course_codes.items():
        # Create a general OneRoster Course
        course_sourced_id = f"sis_course_{code}"
        course = Course(
            sourcedId=course_sourced_id,
            title=sis_course_offering_example['course_title'].split(" - Section")[0],  # Generalize title
            courseCode=code,
            orgSourcedId=f"sis_org_{sis_course_offering_example['school_id']}",  # School offering the course
            schoolYearSourcedId=current_school_year_sid,
            status=StatusType.ACTIVE
            # grades could be derived if available in SIS course data
        )
        oneroster_courses.append(course)

        # Now create OneRoster Classes for each specific offering/section from the original sis_courses_data
        for sis_class_offering in [c for c in sis_courses_data if c['course_code'] == code]:
            # SIS "course_code" might map to a OneRoster "classCode" if sections are implied
            # Or generate a unique class sourcedId
            class_sourced_id = f"sis_class_{sis_class_offering['course_code']}_{sis_class_offering.get('section', '001')}"  # Assuming section if present

            cl = Class(
                sourcedId=class_sourced_id,
                title=sis_class_offering['course_title'],  # Specific title for the class
                classCode=f"{sis_class_offering['course_code']}-{sis_class_offering.get('section', '001')}",
                classType=ClassType.SCHEDULED,  # Assuming scheduled
                courseSourcedId=course_sourced_id,
                schoolSourcedId=f"sis_org_{sis_class_offering['school_id']}",
                termSourcedIds=[current_term_sid],
                status=StatusType.ACTIVE
            )
            oneroster_classes.append(cl)

    return oneroster_courses, oneroster_classes


# Placeholder for Academic Sessions (can be hardcoded for PoC or fetched if SIS provides)
def get_default_academic_sessions() -> List[AcademicSession]:
    now = datetime.utcnow()
    current_year = now.year
    return [
        AcademicSession(
            sourcedId="default_ay_2023-2024",  # Match placeholder used above
            title=f"Academic Year {current_year - 1}-{current_year}",
            startDate=f"{current_year - 1}-08-15",
            endDate=f"{current_year}-06-15",
            type="schoolYear",
            schoolYear=str(current_year - 1),
            status=StatusType.ACTIVE
        ),
        AcademicSession(
            sourcedId="default_term_fall2023",  # Match placeholder
            title=f"Fall Semester {current_year - 1}",
            startDate=f"{current_year - 1}-08-15",
            endDate=f"{current_year - 1}-12-20",
            type="semester",
            parentSourcedId="default_ay_2023-2024",
            schoolYear=str(current_year - 1),
            status=StatusType.ACTIVE
        )
    ]


async def process_sis_to_oneroster() -> Dict[str, List[Any]]:
    """
    Main function for SIS connector: fetches, transforms, and returns OneRoster data.
    """
    sis_orgs_data, sis_students_data, sis_teachers_data, sis_courses_data = await fetch_sis_data()

    oneroster_orgs = transform_sis_orgs(sis_orgs_data)
    oneroster_courses, oneroster_classes = transform_sis_courses_and_classes(sis_courses_data)
    # Pass sis_courses_data to help resolve school for enrollments in this simplified model
    oneroster_users, oneroster_enrollments = transform_sis_users_and_enrollments(
        sis_students_data, sis_teachers_data, sis_courses_data
    )
    oneroster_academic_sessions = get_default_academic_sessions()

    return {
        "orgs": [org.model_dump() for org in oneroster_orgs],
        "users": [user.model_dump() for user in oneroster_users],
        "courses": [course.model_dump() for course in oneroster_courses],
        "classes": [cl.model_dump() for cl in oneroster_classes],
        "enrollments": [enr.model_dump() for enr in oneroster_enrollments],
        "academicSessions": [acad_session.model_dump() for acad_session in oneroster_academic_sessions],
    }