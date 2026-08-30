from pydantic import BaseModel
from typing import Optional


class ReportOut(BaseModel):
    id: str
    institute_id: str
    institute_name: str
    inspector_user_id: str
    inspector_name: str
    beneficiaries_present: int
    beneficiaries_claimed: int
    attendance_status: str  # "matches" | "discrepancy"
    hygiene: str
    notes: Optional[str] = None
    photo_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distance_from_institute_meters: Optional[float] = None
    submitted_at: str
    status: str  # "verified" | "flagged"