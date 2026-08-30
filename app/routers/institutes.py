from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.institute import InstituteCreate, InstituteOut
from app.database import institutes_collection
from app.utils import generate_readable_id
from app.dependencies import require_role, get_current_user

router = APIRouter(prefix="/institutes", tags=["institutes"])


def _to_out(doc: dict) -> InstituteOut:
    return InstituteOut(id=doc["_id"], name=doc["name"], location=doc["location"],
                         beneficiaries=doc["beneficiaries"], rtsp_url=doc.get("rtsp_url"))


@router.post("", response_model=InstituteOut, status_code=status.HTTP_201_CREATED)
async def create_institute(payload: InstituteCreate, current_user: dict = Depends(require_role("admin"))):
    doc = {
        "_id": generate_readable_id("INST"),
        "name": payload.name,
        "location": payload.location,
        "beneficiaries": payload.beneficiaries,
        "rtsp_url": payload.rtsp_url,
    }
    await institutes_collection.insert_one(doc)
    return _to_out(doc)


@router.get("", response_model=List[InstituteOut])
async def list_institutes(current_user: dict = Depends(get_current_user)):
    docs = await institutes_collection.find().to_list(length=500)
    return [_to_out(d) for d in docs]


@router.get("/{institute_id}", response_model=InstituteOut)
async def get_institute(institute_id: str, current_user: dict = Depends(get_current_user)):
    doc = await institutes_collection.find_one({"_id": institute_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institute not found")
    return _to_out(doc)
