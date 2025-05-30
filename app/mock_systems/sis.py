# app/mock_systems/sis.py
from typing import List, Dict, Any

# Sample native SIS data (not OneRoster format yet)
mock_sis_students_data: List[Dict[str, Any]] = [
    {
        "sis_student_id": "S1001",
        "first_name": "Alice",
        "last_name": "Wonderland",
        "grade_level": "5",
        "dob": "2014-07-22",
        "email_address": "alice.w@example.edu",
        "homeroom_teacher_id": "T201",
        "enrollments": [
            {"class_id": "MATH5A", "section": "001"},
            {"class_id": "ELA5A", "section": "001"},
        ],
    },
    {
        "sis_student_id": "S1002",
        "first_name": "Bob",
        "last_name": "TheBuilder",
        "grade_level": "5",
        "dob": "2014-03-15",
        "email_address": "bob.b@example.edu",
        "homeroom_teacher_id": "T201",
        "enrollments": [
            {"class_id": "MATH5A", "section": "001"},
            {"class_id": "SCI5", "section": "002"},
        ],
    },
]

mock_sis_teachers_data: List[Dict[str, Any]] = [
    {
        "sis_teacher_id": "T201",
        "staff_first_name": "Sarah",
        "staff_last_name": "Connor",
        "primary_email": "sconnor@example.edu",
        "department": "Elementary",
        "assigned_classes": [
            {"class_id": "MATH5A", "section": "001", "role": "Primary"},
            {"class_id": "ELA5A", "section": "001", "role": "Primary"},
        ]
    },
    {
        "sis_teacher_id": "T202",
        "staff_first_name": "John",
        "staff_last_name": "Smith",
        "primary_email": "jsmith@example.edu",
        "department": "Science",
        "assigned_classes": [
            {"class_id": "SCI5", "section": "002", "role": "Primary"},
        ]
    },
]

mock_sis_courses_data: List[Dict[str, Any]] = [ # SIS might call these "course offerings" or similar
    {"course_code": "MATH5A", "course_title": "5th Grade Mathematics - Section A", "school_id": "SCH001"},
    {"course_code": "ELA5A", "course_title": "5th Grade English Language Arts - Section A", "school_id": "SCH001"},
    {"course_code": "SCI5", "course_title": "5th Grade Science", "school_id": "SCH001"},
]

mock_sis_orgs_data: List[Dict[str, Any]] = [
    {"org_id": "DIST01", "org_name": "Main Street District", "org_type": "district"},
    {"org_id": "SCH001", "org_name": "Main Street Elementary", "org_type": "school", "parent_org_id": "DIST01"},
]


def get_sis_students() -> List[Dict[str, Any]]:
    # In a real system, this would query a database or another API
    return mock_sis_students_data

def get_sis_teachers() -> List[Dict[str, Any]]:
    return mock_sis_teachers_data

def get_sis_courses() -> List[Dict[str, Any]]:
    return mock_sis_courses_data

def get_sis_orgs() -> List[Dict[str, Any]]:
    return mock_sis_orgs_data