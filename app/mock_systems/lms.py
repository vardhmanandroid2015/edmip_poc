# app/mock_systems/lms.py
from typing import List, Dict, Any

# Sample native LMS data
mock_lms_courses_data: List[Dict[str, Any]] = [
    {
        "lms_course_id": "LMS_M5A_001",
        "course_name": "Mathematics Grade 5 - Morning Block",
        "lms_teacher_username": "sconnor_teacher",
        "external_sis_course_id": "MATH5A", # Optional: for potential linking
        "student_usernames_enrolled": ["alice_w_student", "bob_b_student"],
    },
    {
        "lms_course_id": "LMS_ELA5A_001",
        "course_name": "ELA Grade 5 - Morning Block",
        "lms_teacher_username": "sconnor_teacher",
        "external_sis_course_id": "ELA5A",
        "student_usernames_enrolled": ["alice_w_student"],
    },
    {
        "lms_course_id": "LMS_SCI5_002",
        "course_name": "Science 5 - Afternoon",
        "lms_teacher_username": "jsmith_teacher",
        "external_sis_course_id": "SCI5",
        "student_usernames_enrolled": ["bob_b_student"],
    }
]

mock_lms_users_data: List[Dict[str, Any]] = [
    {"lms_username": "alice_w_student", "full_name": "Alice Wonderland", "role": "student", "email": "alice.w@example.edu"},
    {"lms_username": "bob_b_student", "full_name": "Bob TheBuilder", "role": "student", "email": "bob.b@example.edu"},
    {"lms_username": "sconnor_teacher", "full_name": "Sarah Connor", "role": "instructor", "email": "sconnor@example.edu"},
    {"lms_username": "jsmith_teacher", "full_name": "John Smith", "role": "instructor", "email": "jsmith@example.edu"},
]


def get_lms_courses() -> List[Dict[str, Any]]:
    return mock_lms_courses_data

def get_lms_users() -> List[Dict[str, Any]]:
    return mock_lms_users_data