from pydantic import BaseModel


class AssignmentOut(BaseModel):
    id: str
    institute_id: str
    institute_name: str
    inspector_user_id: str
    inspector_name: str
    window: str
    status: str  # "pending" | "completed"
