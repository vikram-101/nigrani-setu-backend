from pydantic import BaseModel


class AlertOut(BaseModel):
    id: str
    type: str
    institute_id: str
    institute_name: str
    report_id: str
    detail: str
    severity: str  # "high" | "low"
    created_at: str
