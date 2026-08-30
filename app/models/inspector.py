from pydantic import BaseModel


class InspectorOut(BaseModel):
    id: str
    user_id: str
    name: str
    district: str
