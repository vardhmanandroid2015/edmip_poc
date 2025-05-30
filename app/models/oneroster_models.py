# app/models/oneroster_models.py
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any, Union
from enum import Enum
import uuid # For generating sourcedIds if needed
from datetime import datetime

# --- Enums for OneRoster fields ---
class StatusType(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TOBEDELETED = "tobedeleted"

class RoleType(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMINISTRATOR = "administrator"
    GUARDIAN = "guardian"
    AIDE = "aide"
    RELATIVE = "relative"
    PARENT = "parent" # Though 'guardian' or 'relative' is often preferred in v1.1 for specifics

class OrgType(str, Enum):
    DISTRICT = "district"
    SCHOOL = "school"
    LOCAL = "local" # equivalent to district
    STATE = "state"
    NATIONAL = "national"

class ClassType(str, Enum):
    HOMEROOM = "homeroom"
    SCHEDULED = "scheduled"

# --- Base Model for common OneRoster fields ---
class OneRosterBase(BaseModel):
    sourcedId: str
    status: StatusType = StatusType.ACTIVE
    dateLastModified: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    metadata: Optional[Dict[str, Any]] = None

# --- Specific OneRoster Entity Models ---
class Org(OneRosterBase):
    name: str
    type: OrgType
    identifier: Optional[str] = None
    parentSourcedId: Optional[str] = None # Technically a "orgPointer" but string for simplicity here

class User(OneRosterBase):
    username: str
    userIds: Optional[List[Dict[str, str]]] = None # e.g., [{"type": "SSN", "identifier": "xxx-xx-xxxx"}]
    enabledUser: bool = True
    givenName: str
    familyName: str
    middleName: Optional[str] = None
    role: RoleType
    identifier: Optional[str] = None # Often the same as a primary userId identifier
    email: Optional[str] = None
    sms: Optional[str] = None
    phone: Optional[str] = None
    agentSourcedIds: List[str] = Field(default_factory=list) # List of org sourcedIds
    grades: Optional[List[str]] = None # e.g., ["05", "KG"]
    # password: Optional[str] = None # Usually not part of roster exchange for security

class Course(OneRosterBase):
    title: str
    schoolYearSourcedId: Optional[str] = None
    courseCode: Optional[str] = None
    grades: Optional[List[str]] = None
    orgSourcedId: Optional[str] = None
    subjects: Optional[List[str]] = None
    subjectCodes: Optional[List[str]] = None

class Class(OneRosterBase):
    title: str
    classCode: Optional[str] = None
    classType: ClassType
    location: Optional[str] = None
    grades: Optional[List[str]] = None
    subjects: Optional[List[str]] = None
    courseSourcedId: str # Link to a Course
    schoolSourcedId: str # Link to an Org (school)
    termSourcedIds: List[str] = Field(default_factory=list) # Link to AcademicSession(s)
    periods: Optional[List[str]] = None

class Enrollment(OneRosterBase):
    userSourcedId: str
    classSourcedId: str
    schoolSourcedId: str
    role: RoleType
    primary: Optional[bool] = None
    beginDate: Optional[str] = None # YYYY-MM-DD
    endDate: Optional[str] = None   # YYYY-MM-DD

class AcademicSession(OneRosterBase):
    title: str
    startDate: str # YYYY-MM-DD
    endDate: str   # YYYY-MM-DD
    type: str # e.g., "gradingPeriod", "semester", "schoolYear", "term"
    parentSourcedId: Optional[str] = None
    schoolYear: Optional[str] = None # e.g., "2023" for 2023-2024 school year

# Container for all processed OneRoster data
class ProcessedOneRosterData(BaseModel):
    orgs: List[Org] = Field(default_factory=list)
    users: List[User] = Field(default_factory=list)
    courses: List[Course] = Field(default_factory=list)
    classes: List[Class] = Field(default_factory=list)
    enrollments: List[Enrollment] = Field(default_factory=list)
    academicSessions: List[AcademicSession] = Field(default_factory=list)
    # Add demographics, resources etc. as needed

class Course(OneRosterBase):
    title: str
    schoolYearSourcedId: Optional[str] = None
    courseCode: Optional[str] = None
    grades: Optional[List[str]] = None
    orgSourcedId: Optional[str] = None # School that offers this course definition
    subjects: Optional[List[str]] = None
    subjectCodes: Optional[List[str]] = None