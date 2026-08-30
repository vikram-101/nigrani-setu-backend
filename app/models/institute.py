from pydantic import BaseModel
from typing import Optional


class InstituteCreate(BaseModel):
    name: str
    location: str
    beneficiaries: int
    rtsp_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class InstituteOut(BaseModel):
    id: str
    name: str
    location: str
    beneficiaries: int
    rtsp_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None