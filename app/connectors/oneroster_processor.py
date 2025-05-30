# app/connectors/oneroster_processor.py
from typing import Dict, List, Any
from app.connectors import sis_connector
from app.connectors import lms_connector  # Import the new LMS connector
from app.models.oneroster_models import ProcessedOneRosterData, User as OneRosterUser, Course as OneRosterCourse


async def get_processed_oneroster_data() -> ProcessedOneRosterData:
    """
    Orchestrates fetching and transforming data from all source systems
    and returns a consolidated OneRoster dataset.
    """
    # Fetch and transform SIS data (considered primary for OneRoster structure)
    sis_oneroster_data_dict = await sis_connector.process_sis_to_oneroster()

    # Fetch and transform LMS data into OneRoster-like structures
    lms_oneroster_like_data_dict = await lms_connector.process_lms_to_oneroster_like_data()

    lms_users: List[OneRosterUser] = [OneRosterUser(**u) for u in lms_oneroster_like_data_dict.get("users", [])]
    lms_courses: List[OneRosterCourse] = [OneRosterCourse(**c) for c in lms_oneroster_like_data_dict.get("courses", [])]

    print(f"Retrieved {len(lms_users)} users from LMS connector.")
    print(f"Retrieved {len(lms_courses)} courses from LMS connector.")

    # --- Data Merging/Reconciliation Logic (Placeholder for future enhancement) ---
    # This is where you would implement logic to:
    # 1. Match users from SIS and LMS (e.g., by email, or a common identifier).
    # 2. Merge or augment user profiles (e.g., add LMS username to SIS user metadata).
    # 3. Match courses between SIS and LMS.
    # 4. Decide on the authoritative source for conflicting information.
    #
    # For this PoC phase, we will primarily use the SIS-derived OneRoster data as the base.
    # The LMS data is fetched and transformed but not deeply integrated into the final output yet.
    # We could, for example, add LMS metadata to SIS users if a match is found.

    # Example: Add LMS username as metadata to matched SIS users (very basic matching by email)
    final_users_list = []
    sis_users_from_dict = sis_oneroster_data_dict.get("users", [])

    for sis_user_dict in sis_users_from_dict:
        sis_user_obj = OneRosterUser(**sis_user_dict)
        matched_lms_user = next((lms_u for lms_u in lms_users if
                                 lms_u.email and sis_user_obj.email and lms_u.email.lower() == sis_user_obj.email.lower()),
                                None)
        if matched_lms_user:
            if sis_user_obj.metadata is None:
                sis_user_obj.metadata = {}
            sis_user_obj.metadata["lms_username"] = matched_lms_user.username
            sis_user_obj.metadata["lms_sourcedId"] = matched_lms_user.sourcedId
            print(f"Matched SIS user {sis_user_obj.sourcedId} with LMS user {matched_lms_user.sourcedId} by email.")
        final_users_list.append(sis_user_obj.model_dump())  # Convert back to dict for ProcessedOneRosterData

    # For other entities, we're still using SIS as primary for now
    processed_data = ProcessedOneRosterData(
        orgs=sis_oneroster_data_dict.get("orgs", []),
        users=final_users_list,  # Use the potentially augmented user list
        courses=sis_oneroster_data_dict.get("courses", []),  # Could also try to merge/augment courses
        classes=sis_oneroster_data_dict.get("classes", []),
        enrollments=sis_oneroster_data_dict.get("enrollments", []),
        academicSessions=sis_oneroster_data_dict.get("academicSessions", [])
    )

    return processed_data