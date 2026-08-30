from pydantic import BaseModel
from typing import Optional


class InstituteCreate(BaseModel):
    name: str
    location: str
    beneficiaries: int
    rtsp_url: Optional[str] = None


class InstituteOut(BaseModel):
    id: str
    name: str
    location: str
    beneficiaries: int
    rtsp_url: Optional[str] = None
